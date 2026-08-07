import os
os.environ['SQLITE_FALLBACK'] = '1'

import asyncio, sys, uuid
sys.path.append('/mnt/shared/Projects/Metis')
from server.database.connection import async_session_factory
from server.repositories.job_repository import JobRepository
from sqlalchemy import select, func
from server.database.models import User, ProcessingJob

async def test():
    async with async_session_factory() as db:
        user = (await db.execute(select(User).limit(1))).scalar()
        if not user: return
        print("User:", user.id)
        
        # Total jobs ANY date
        stmt_total = select(func.count(ProcessingJob.id)).where(ProcessingJob.user_id == user.id)
        total = (await db.execute(stmt_total)).scalar() or 0
        print("Total jobs ANY date:", total)
        
        # Total jobs with naive utcnow
        from datetime import datetime, timedelta
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        stmt_total_30 = select(func.count(ProcessingJob.id)).where(ProcessingJob.user_id == user.id, ProcessingJob.created_at >= thirty_days_ago)
        total_30 = (await db.execute(stmt_total_30)).scalar() or 0
        print("Total jobs 30 days ago:", total_30)

        # Print all created_at values
        stmt_dates = select(ProcessingJob.created_at).where(ProcessingJob.user_id == user.id)
        dates = (await db.execute(stmt_dates)).scalars().all()
        print("Dates:", dates)

asyncio.run(test())
