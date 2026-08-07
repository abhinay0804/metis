import os
import asyncio
from celery import Celery
import time
import json
import logging

# We need to run some async code in Celery which is synchronous by default
# We'll use a new event loop
def run_async(coro):
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    if loop.is_running():
        # Fallback if somehow called within a running loop
        import threading
        result = None
        def _run():
            nonlocal result
            new_loop = asyncio.new_event_loop()
            result = new_loop.run_until_complete(coro)
            new_loop.close()
        t = threading.Thread(target=_run)
        t.start()
        t.join()
        return result
    else:
        return loop.run_until_complete(coro)

redis_url = os.getenv("CELERY_BROKER_URL", os.getenv("REDIS_URL", "redis://localhost:6379/0"))
celery_app = Celery("metis_tasks", broker=redis_url, backend=redis_url)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="process_file_task")
def process_file_task(self, job_id: str, file_path: str, filename: str, reversible: bool = False, user_id: str = ""):
    """
    Background task to process a file: Extract -> Mask -> (Encrypt Original if reversible) -> Save
    """
    logger.info(f"Starting async processing for job {job_id} (reversible={reversible})")
    
    try:
        # Since we use SQLAlchemy Async engine and other async utils, 
        # we need to import them inside the task and run via asyncio
        from server.file_processor import FileProcessor
        from server.sensitive_data_masking import SensitiveDataMasker
        from server.database.connection import async_session_factory
        from server.repositories.job_repository import JobRepository
        from server.repositories.result_repository import ResultRepository
        import uuid
        
        # 1. Update job status to EXTRACTING
        async def update_status_func(status, error=None):
            async with async_session_factory() as db:
                job_repo = JobRepository(db)
                await job_repo.update_status(str(job_id), status, error_message=error)
        
        run_async(update_status_func("extracting"))
        
        # Notify via redis pubsub so the websocket manager can broadcast it
        import redis
        r = redis.from_url(redis_url)
        r.publish('job_updates', json.dumps({"job_id": job_id, "status": "extracting", "message": "Extracting text..."}))
        
        # 2. Extract Text
        start_time = time.time()
        
        processor = FileProcessor(use_model_detector=False)
        extraction_result = processor.process_file(file_path, mask_sensitive=False)
        
        metadata = extraction_result.get("extraction_metadata", {})
        if not metadata.get("success"):
            run_async(update_status_func("failed", metadata.get("error", "Extraction failed")))
            r.publish('job_updates', json.dumps({"job_id": job_id, "status": "failed", "message": "Extraction failed"}))
            return {"success": False, "error": metadata.get("error")}
            
        extracted_content = extraction_result.get("content", {})
        
        # 2.5. If reversible, encrypt and store original content BEFORE masking
        if reversible and user_id:
            try:
                from reversible.storage_reversible import EncryptedLocalStore
                enc_store = EncryptedLocalStore(base_dir=os.path.join(os.getcwd(), "reversible"))
                enc_store.store_original(user_id, job_id, extracted_content)
                
                # Read back the encrypted blob to save in DB
                enc_path = enc_store._data_path(user_id, job_id)
                with open(enc_path, 'rb') as ef:
                    encrypted_blob = ef.read()
                
                async def save_original_to_db():
                    async with async_session_factory() as db:
                        result_repo = ResultRepository(db)
                        await result_repo.save_original(
                            job_id=job_id,
                            encrypted_content=encrypted_blob,
                            encryption_key_id=user_id,
                        )
                
                run_async(save_original_to_db())
                logger.info(f"Reversible: encrypted original stored for job {job_id}")
            except Exception as enc_err:
                logger.warning(f"Reversible encryption failed (non-fatal): {enc_err}")
        
        # 3. Mask Text
        run_async(update_status_func("masking"))
        r.publish('job_updates', json.dumps({"job_id": job_id, "status": "masking", "message": "Masking sensitive data..."}))
        
        masker = SensitiveDataMasker()
        masked_content = masker.mask_sensitive_data(extracted_content)
        
        # Ensure we always wrap the content in a dict before saving to JSON column
        if isinstance(masked_content, str):
            masked_content = {"content": masked_content}
            
        stats = masker.generate_masking_report(extracted_content)
        
        # 4. Save Results
        run_async(update_status_func("saving"))
        r.publish('job_updates', json.dumps({"job_id": job_id, "status": "saving", "message": "Saving results..."}))
        
        processing_ms = int((time.time() - start_time) * 1000)
        
        async def save_results():
            async with async_session_factory() as db:
                result_repo = ResultRepository(db)
                job_repo = JobRepository(db)
                
                # Save result
                await result_repo.save_masked(
                    job_id=job_id,
                    masked_content=masked_content,
                    detection_summary=stats
                )
                
                # Update job to COMPLETED
                await job_repo.update_status(
                    str(job_id), 
                    "completed", 
                    processing_time_ms=processing_ms
                )
        
        run_async(save_results())
        
        # We can safely delete the temp file now
        if os.path.exists(file_path):
            os.remove(file_path)
            
        r.publish('job_updates', json.dumps({"job_id": job_id, "status": "completed", "message": "Processing finished!"}))
        logger.info(f"Successfully processed job {job_id} in {processing_ms}ms")
        
        return {"success": True, "job_id": job_id, "processing_ms": processing_ms}
        
    except Exception as e:
        logger.error(f"Error processing job {job_id}: {str(e)}")
        # Try to mark as failed
        try:
            run_async(update_status_func("failed", str(e)))
            import redis
            r = redis.from_url(redis_url)
            r.publish('job_updates', json.dumps({"job_id": job_id, "status": "failed", "message": str(e)}))
        except:
            pass
        return {"success": False, "error": str(e)}
