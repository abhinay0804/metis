from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from server.database.models import MaskedResult, OriginalStore
import uuid
from datetime import datetime, timezone

class ResultRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def save_masked(self, job_id: str, masked_content: dict, detection_summary: dict | None = None, confidence_scores: dict | None = None) -> MaskedResult:
        try:
            job_uuid = uuid.UUID(job_id)
        except ValueError:
            raise ValueError("Invalid job_id format")

        new_masked = MaskedResult(
            job_id=job_uuid,
            masked_content=masked_content,
            detection_summary=detection_summary or {},
            confidence_scores=confidence_scores or {},
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(new_masked)
        await self.session.commit()
        await self.session.refresh(new_masked)
        return new_masked

    async def get_masked_by_job(self, job_id: str) -> MaskedResult | None:
        try:
            job_uuid = uuid.UUID(job_id)
        except ValueError:
            return None
        stmt = select(MaskedResult).where(MaskedResult.job_id == job_uuid)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def save_original(self, job_id: str, encrypted_content: bytes, encryption_key_id: str) -> OriginalStore:
        try:
            job_uuid = uuid.UUID(job_id)
        except ValueError:
            raise ValueError("Invalid job_id format")

        new_original = OriginalStore(
            job_id=job_uuid,
            encrypted_content=encrypted_content,
            encryption_key_id=encryption_key_id,
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(new_original)
        await self.session.commit()
        await self.session.refresh(new_original)
        return new_original

    async def get_original_by_job(self, job_id: str) -> OriginalStore | None:
        try:
            job_uuid = uuid.UUID(job_id)
        except ValueError:
            return None
        stmt = select(OriginalStore).where(OriginalStore.job_id == job_uuid)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
