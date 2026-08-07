from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from sqlalchemy.orm import selectinload
from server.database.models import ProcessingJob, MaskedResult
import uuid
from datetime import datetime, timezone, timedelta
from typing import Optional

class JobRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, user_id: str, file_name: str, file_type: str, job_type: str = 'masking', file_size_bytes: int | None = None) -> ProcessingJob:
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            raise ValueError("Invalid user_id format")

        new_job = ProcessingJob(
            user_id=user_uuid,
            file_name=file_name,
            file_type=file_type,
            job_type=job_type,
            file_size_bytes=file_size_bytes,
            status='pending',
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(new_job)
        await self.session.commit()
        await self.session.refresh(new_job)
        return new_job

    async def get_by_id(self, job_id: str) -> ProcessingJob | None:
        try:
            job_uuid = uuid.UUID(job_id)
        except ValueError:
            return None
        stmt = select(ProcessingJob).where(ProcessingJob.id == job_uuid)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_status(self, job_id: str, status: str, processing_time_ms: int | None = None, error_message: str | None = None) -> ProcessingJob | None:
        job = await self.get_by_id(job_id)
        if job:
            job.status = status
            if processing_time_ms is not None:
                job.processing_time_ms = processing_time_ms
            if error_message is not None:
                job.error_message = error_message
            if status in ['completed', 'failed']:
                job.completed_at = datetime.now(timezone.utc)
            await self.session.commit()
            await self.session.refresh(job)
        return job

    async def list_by_user(self, user_id: str, skip: int = 0, limit: int = 20, status: str | None = None) -> list[dict]:
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return []

        stmt = select(ProcessingJob).options(selectinload(ProcessingJob.original_store)).where(ProcessingJob.user_id == user_uuid)
        if status:
            stmt = stmt.where(ProcessingJob.status == status)
        
        stmt = stmt.order_by(desc(ProcessingJob.created_at)).offset(skip).limit(limit)
        result = await self.session.execute(stmt)
        jobs = result.scalars().all()
        
        job_list = []
        for job in jobs:
            job_list.append({
                "job_id": str(job.id),
                "file_name": job.file_name,
                "file_type": job.file_type,
                "job_type": job.job_type,
                "file_size_bytes": job.file_size_bytes,
                "status": job.status,
                "processing_time_ms": job.processing_time_ms,
                "created_at": (job.created_at.isoformat() + "Z") if job.created_at and not job.created_at.tzinfo else (job.created_at.isoformat() if job.created_at else None),
                "completed_at": (job.completed_at.isoformat() + "Z") if job.completed_at and not job.completed_at.tzinfo else (job.completed_at.isoformat() if job.completed_at else None),
                "is_reversible": job.original_store.is_reversible if job.original_store else False
            })
        return job_list

    async def get_user_stats(self, user_id: str) -> dict:
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return {
                "total_jobs": 0, 
                "completed_jobs": 0, 
                "failed_jobs": 0, 
                "avg_processing_time_ms": None, 
                "total_pii_detections": 0
            }

        # Use naive UTC time so SQLite lexical comparison works against its stored strings
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)

        stmt_total = select(func.count(ProcessingJob.id)).where(ProcessingJob.user_id == user_uuid, ProcessingJob.created_at >= thirty_days_ago)
        stmt_completed = select(func.count(ProcessingJob.id)).where(ProcessingJob.user_id == user_uuid, ProcessingJob.status == 'completed', ProcessingJob.created_at >= thirty_days_ago)
        stmt_failed = select(func.count(ProcessingJob.id)).where(ProcessingJob.user_id == user_uuid, ProcessingJob.status == 'failed', ProcessingJob.created_at >= thirty_days_ago)
        stmt_avg_time = select(func.avg(ProcessingJob.processing_time_ms)).where(ProcessingJob.user_id == user_uuid, ProcessingJob.status == 'completed', ProcessingJob.created_at >= thirty_days_ago)
        
        total = (await self.session.execute(stmt_total)).scalar() or 0
        completed = (await self.session.execute(stmt_completed)).scalar() or 0
        failed = (await self.session.execute(stmt_failed)).scalar() or 0
        avg_time = (await self.session.execute(stmt_avg_time)).scalar()

        stmt_results = select(MaskedResult.detection_summary).join(ProcessingJob, MaskedResult.job_id == ProcessingJob.id).where(ProcessingJob.user_id == user_uuid, ProcessingJob.created_at >= thirty_days_ago)
        results = await self.session.execute(stmt_results)
        summaries = results.scalars().all()
        
        total_pii = 0
        for summary in summaries:
            if summary and isinstance(summary, dict):
                if 'total' in summary:
                    total_pii += int(summary['total'])
                else:
                    total_pii += sum(int(v) for v in summary.values() if isinstance(v, (int, float, str)) and str(v).isdigit())
        
        return {
            "total_jobs": total,
            "completed_jobs": completed,
            "failed_jobs": failed,
            "avg_processing_time_ms": float(avg_time) if avg_time is not None else None,
            "total_pii_detections": total_pii
        }
