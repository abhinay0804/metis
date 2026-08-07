import asyncio, sys
sys.path.append('/mnt/shared/Projects/Metis')
from server.database.connection import async_session_factory
from server.repositories.job_repository import JobRepository
from sqlalchemy import select, func
from server.database.models import ProcessingJob, User

async def test():
    async with async_session_factory() as db:
        user = (await db.execute(select(User).limit(1))).scalar()
        if not user:
            print("No user")
            return
        repo = JobRepository(db)
        stats = await repo.get_user_stats(str(user.id))
        print("Stats:", stats)

asyncio.run(test())
