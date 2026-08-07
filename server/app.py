"""
Metis — Masking API
FastAPI application with JWT auth, PostgreSQL storage, Celery async workers, Redis caching, and WebSockets.
"""
import os
import uuid
import time
from typing import Optional
from datetime import datetime, timezone

from fastapi import (
    FastAPI, UploadFile, File, Form, Depends, HTTPException, Query, BackgroundTasks, 
    WebSocket, WebSocketDisconnect, Request, Response, Header
)
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from server.file_processor import FileProcessor
from server.sensitive_data_masking import SensitiveDataMasker

from .auth import (
    User, UserRegister, UserLogin, TokenResponse,
    get_current_user, verify_id_token,
    hash_password, verify_password, validate_password,
    create_access_token, create_refresh_token, decode_token,
)
from .database.connection import get_db, init_db
from .database.models import User as UserModel
from .repositories import UserRepository, JobRepository, ResultRepository
from .cache import cache_service
from .websocket import ws_manager
from microservices.tasks import process_file_task

# Analyzer instantiated per request
try:
    from .analysis.gemini_analyzer import GeminiAnalyzer
except ImportError:
    GeminiAnalyzer = None


app = FastAPI(
    title="Metis — PII Detection & Document Masking API",
    description="Enterprise-grade document processing with fine-tuned NER, ensemble PII detection, and real-time masking.",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# Startup & Shutdown
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def on_startup():
    await init_db()
    
    # SQLite automatic schema migration for photo_base64
    import sqlite3
    try:
        conn = sqlite3.connect('metis.db')
        conn.execute("ALTER TABLE users ADD COLUMN photo_base64 TEXT;")
        conn.commit()
        conn.close()
    except Exception:
        pass  # Column likely already exists
        
    await cache_service.connect()

@app.on_event("shutdown")
async def on_shutdown():
    await cache_service.disconnect()


# ---------------------------------------------------------------------------
# Pydantic response models
# ---------------------------------------------------------------------------
class HealthResponse(BaseModel):
    status: str
    version: str = "2.0.0"

class ProcessResponse(BaseModel):
    job_id: str
    status: str
    message: str
    cached: bool = False
    result: Optional[dict] = None

class HistoryItem(BaseModel):
    job_id: str
    file_name: str
    file_type: str
    job_type: str = "masking"
    file_size_bytes: int | None = None
    status: str
    processing_time_ms: int | None = None
    created_at: str
    completed_at: str | None = None
    is_reversible: bool = False

class StatsResponse(BaseModel):
    total_jobs: int
    completed_jobs: int
    failed_jobs: int
    avg_processing_time_ms: float | None = None
    total_pii_detections: int = 0

class UserProfile(BaseModel):
    uid: str
    email: str | None
    full_name: str | None
    phone: str | None
    company: str | None
    department: str | None
    country: str | None
    role: str
    created_at: str
    photo_base64: str | None = None

class ProfileUpdate(BaseModel):
    full_name: str | None = None
    phone: str | None = None
    company: str | None = None
    department: str | None = None
    country: str | None = None

# ===========================================================================
# AUTH ENDPOINTS
# ===========================================================================
@app.post("/auth/register", response_model=TokenResponse)
async def register(body: UserRegister, db: AsyncSession = Depends(get_db)):
    if not validate_password(body.password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters with 1 uppercase letter and 1 digit",
        )
    user_repo = UserRepository(db)
    existing = await user_repo.get_by_email(body.email)
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")
    hashed = hash_password(body.password)
    user = await user_repo.create(
        email=body.email,
        password_hash=hashed,
        full_name=body.full_name,
    )
    access = create_access_token(str(user.id), user.email)
    refresh = create_refresh_token(str(user.id))
    return TokenResponse(access_token=access, refresh_token=refresh)

@app.post("/auth/login", response_model=TokenResponse)
async def login(body: UserLogin, db: AsyncSession = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_email(body.email)
    if not user or not verify_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is disabled")
    await user_repo.update_last_login(str(user.id))
    access = create_access_token(str(user.id), user.email)
    refresh = create_refresh_token(str(user.id))
    return TokenResponse(access_token=access, refresh_token=refresh)

@app.post("/auth/refresh", response_model=TokenResponse)
async def refresh_access_token(
    refresh_token_str: str = Form(..., alias="refresh_token"),
    db: AsyncSession = Depends(get_db),
):
    payload = decode_token(refresh_token_str)
    if payload.type != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token type — expected refresh token")
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(payload.sub)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    access = create_access_token(str(user.id), user.email)
    refresh = create_refresh_token(str(user.id))
    return TokenResponse(access_token=access, refresh_token=refresh)

@app.get("/auth/me", response_model=UserProfile)
async def get_me(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(current_user.uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserProfile(
        uid=str(user.id),
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        company=user.company,
        department=user.department,
        country=user.country,
        role=user.role,
        created_at=(user.created_at.isoformat() + "Z") if not user.created_at.tzinfo else user.created_at.isoformat(),
        photo_base64=user.photo_base64,
    )

class PhotoUpload(BaseModel):
    photo_base64: str

@app.post("/auth/photo", response_model=UserProfile)
async def update_photo(
    body: PhotoUpload,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(current_user.uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    user.photo_base64 = body.photo_base64
    await db.commit()
    await db.refresh(user)
    
    return UserProfile(
        uid=str(user.id),
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        company=user.company,
        department=user.department,
        country=user.country,
        role=user.role,
        created_at=(user.created_at.isoformat() + "Z") if not user.created_at.tzinfo else user.created_at.isoformat(),
        photo_base64=user.photo_base64,
    )

@app.put("/auth/me", response_model=UserProfile)
async def update_me(
    body: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    user_repo = UserRepository(db)
    user = await user_repo.get_by_id(current_user.uid)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if body.full_name is not None:
        user.full_name = body.full_name
    if body.phone is not None:
        user.phone = body.phone
    if body.company is not None:
        user.company = body.company
    if body.department is not None:
        user.department = body.department
    if body.country is not None:
        user.country = body.country
        
    await db.commit()
    
    return UserProfile(
        uid=str(user.id),
        email=user.email,
        full_name=user.full_name,
        phone=user.phone,
        company=user.company,
        department=user.department,
        country=user.country,
        role=user.role,
        created_at=user.created_at.isoformat(),
    )



# ===========================================================================
# FILE PROCESSING ENDPOINTS
# ===========================================================================
@app.get("/health", response_model=HealthResponse)
def health():
    return HealthResponse(status="ok")

@app.post("/process", response_model=ProcessResponse, status_code=202)
async def process_file(
    file: UploadFile = File(...),
    reversible: bool = Form(False),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a file for processing. Checks Redis cache first.
    If not cached, creates a job and dispatches a Celery task.
    """
    contents = await file.read()
    file_size = len(contents)
    
    # 1. Check Redis Cache
    file_hash = cache_service.compute_hash(contents)
    cached_result = await cache_service.get_cached_result(file_hash)
    
    if cached_result:
        # We got a cache hit! Fast path.
        job_repo = JobRepository(db)
        result_repo = ResultRepository(db)
        
        # Create a job record that's instantly completed
        job = await job_repo.create(
            user_id=current_user.uid,
            file_name=file.filename,
            file_type=cached_result.get("file_type", "unknown"),
            file_size_bytes=file_size,
        )
        job_id = str(job.id)
        await job_repo.update_status(job_id, "completed", processing_time_ms=0)
        
        cached_masked = cached_result.get("masked_content", {})
        if isinstance(cached_masked, str):
            cached_masked = {"content": cached_masked}
            
        await result_repo.save_masked(
            job_id=job_id,
            masked_content=cached_masked,
            detection_summary=cached_result.get("detection_summary", {}),
        )
        
        return ProcessResponse(
            job_id=job_id,
            status="completed",
            message="Returned instantly from cache",
            cached=True,
            result=cached_result
        )

    # 2. No cache hit. Save to disk and start async job
    tmp_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, f"{uuid.uuid4()}_{file.filename}")
    
    with open(tmp_path, "wb") as f:
        f.write(contents)

    job_repo = JobRepository(db)
    job = await job_repo.create(
        user_id=current_user.uid,
        file_name=file.filename,
        file_type="unknown",
        file_size_bytes=file_size,
    )
    job_id = str(job.id)
    await job_repo.update_status(job_id, "pending")

    # Dispatch Celery Task
    process_file_task.delay(job_id, tmp_path, file.filename, reversible, current_user.uid)

    return ProcessResponse(
        job_id=job_id,
        status="pending",
        message="Job queued for async processing. Connect to websocket for updates.",
        cached=False
    )


@app.post("/analyze", status_code=200)
async def analyze_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    x_gemini_api_key: str = Header(None, alias="X-Gemini-API-Key"),
):
    """
    Synchronously analyze the uploaded file using QualityContentAnalyzer.
    """
    if not GeminiAnalyzer:
        raise HTTPException(status_code=501, detail="Analyzer module not available")
        
    if not x_gemini_api_key:
        raise HTTPException(status_code=400, detail="Gemini API Key is required in X-Gemini-API-Key header")

    contents = await file.read()
    
    # Save to temp path for extraction
    tmp_dir = os.path.join(os.getcwd(), "uploads")
    os.makedirs(tmp_dir, exist_ok=True)
    tmp_path = os.path.join(tmp_dir, f"analyze_{uuid.uuid4()}_{file.filename}")
    
    with open(tmp_path, "wb") as f:
        f.write(contents)
        
    try:
        processor = FileProcessor(use_model_detector=True, enable_logo_redaction=True, enable_ocr=True)
        file_type = processor.get_file_type(tmp_path)
        
        extractor = processor.extractors.get(file_type)
        if not extractor:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {file_type}")
            
        if hasattr(extractor, "extract"):
            if file_type == "application/pdf":
                extracted_content = extractor.extract(tmp_path, enable_ocr=True)
            else:
                extracted_content = extractor.extract(tmp_path)
        else:
            raise HTTPException(status_code=500, detail="Invalid extractor")
            
        start_time = time.time()
        # Run analysis
        analyzer = GeminiAnalyzer(api_key=x_gemini_api_key)
        try:
            analysis_result = analyzer.analyze(extracted_content, file_type)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))
            
        processing_time_ms = int((time.time() - start_time) * 1000)
        
        # Add a job record for history
        job_repo = JobRepository(db)
        job = await job_repo.create(
            user_id=current_user.uid,
            file_name=file.filename,
            file_type=file_type,
            job_type="analysis",
            file_size_bytes=len(contents),
        )
        job_id = str(job.id)
        await job_repo.update_status(job_id, "completed", processing_time_ms=processing_time_ms)
        
        # Save analysis to result_repo so it shows up in history
        result_repo = ResultRepository(db)
        await result_repo.save_masked(
            job_id=job_id,
            masked_content={"analysis_only": True},
            detection_summary=analysis_result
        )
        
        return analysis_result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)


# ===========================================================================
# WEBSOCKET ENDPOINT
# ===========================================================================
@app.websocket("/ws/jobs/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await ws_manager.connect(websocket, job_id)
    try:
        while True:
            # We keep the connection open. The Redis pubsub listener (if implemented in a separate background task)
            # or Celery tasks themselves broadcast to this manager.
            # For this simple implementation, the client just waits for messages pushed from elsewhere.
            data = await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket, job_id)


# ===========================================================================
# HISTORY & RETRIEVAL ENDPOINTS
# ===========================================================================
@app.get("/history", response_model=list[HistoryItem])
async def get_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job_repo = JobRepository(db)
    jobs = await job_repo.list_by_user(
        user_id=current_user.uid,
        skip=skip,
        limit=limit,
        status=status,
    )
    return [HistoryItem(**j) for j in jobs]

@app.get("/history/{job_id}")
async def get_job_detail(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job_repo = JobRepository(db)
    result_repo = ResultRepository(db)
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if str(job.user_id) != current_user.uid and current_user.uid != "dev-user":
        raise HTTPException(status_code=403, detail="Access denied")
    masked = await result_repo.get_masked_by_job(job_id)
    original = await result_repo.get_original_by_job(job_id)
    return {
        "job_id": str(job.id),
        "file_name": job.file_name,
        "file_type": job.file_type,
        "file_size_bytes": job.file_size_bytes,
        "status": job.status,
        "processing_time_ms": job.processing_time_ms,
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
        "error_message": job.error_message,
        "masked_content": masked.masked_content if masked else None,
        "detection_summary": masked.detection_summary if masked else None,
        "is_reversible": original.is_reversible if original else False,
    }

@app.get("/dashboard-data", response_model=StatsResponse)
async def get_stats(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    job_repo = JobRepository(db)
    stats = await job_repo.get_user_stats(current_user.uid)
    return StatsResponse(**stats)


@app.post("/unmask/{job_id}")
async def unmask_job(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Decrypt and return the original unmasked content for a reversible masking job.
    """
    job_repo = JobRepository(db)
    result_repo = ResultRepository(db)
    job = await job_repo.get_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    if str(job.user_id) != current_user.uid and current_user.uid != "dev-user":
        raise HTTPException(status_code=403, detail="Access denied")

    original = await result_repo.get_original_by_job(job_id)
    if not original or not original.is_reversible:
        raise HTTPException(status_code=404, detail="No reversible data stored for this job")

    # Decrypt using the EncryptedLocalStore
    from reversible.storage_reversible import EncryptedLocalStore
    store = EncryptedLocalStore(base_dir=os.path.join(os.getcwd(), "reversible"))
    try:
        original_content = store.load_original(original.encryption_key_id, job_id)
        return {"job_id": job_id, "original_content": original_content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Decryption failed: {str(e)}")
