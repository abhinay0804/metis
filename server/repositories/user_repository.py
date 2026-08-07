from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from server.database.models import User, ProcessingJob
import uuid
from datetime import datetime, timezone

class UserRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, email: str, password_hash: str, full_name: str | None = None) -> User:
        new_user = User(
            email=email,
            password_hash=password_hash,
            full_name=full_name,
            created_at=datetime.now(timezone.utc),
        )
        self.session.add(new_user)
        await self.session.commit()
        await self.session.refresh(new_user)
        return new_user

    async def get_by_id(self, user_id: str) -> User | None:
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return None
        stmt = select(User).where(User.id == user_uuid)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def update_last_login(self, user_id: str) -> None:
        user = await self.get_by_id(user_id)
        if user:
            user.last_login = datetime.now(timezone.utc)
            await self.session.commit()

    async def get_stats(self, user_id: str) -> dict:
        try:
            user_uuid = uuid.UUID(user_id)
        except ValueError:
            return {"total_jobs": 0, "completed_jobs": 0, "failed_jobs": 0}
            
        stmt_total = select(func.count(ProcessingJob.id)).where(ProcessingJob.user_id == user_uuid)
        stmt_completed = select(func.count(ProcessingJob.id)).where(ProcessingJob.user_id == user_uuid, ProcessingJob.status == 'completed')
        stmt_failed = select(func.count(ProcessingJob.id)).where(ProcessingJob.user_id == user_uuid, ProcessingJob.status == 'failed')
        
        total = (await self.session.execute(stmt_total)).scalar() or 0
        completed = (await self.session.execute(stmt_completed)).scalar() or 0
        failed = (await self.session.execute(stmt_failed)).scalar() or 0
        
        return {
            "total_jobs": total,
            "completed_jobs": completed,
            "failed_jobs": failed
        }
