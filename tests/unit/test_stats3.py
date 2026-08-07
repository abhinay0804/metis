import os, asyncio, sys
os.environ['SQLITE_FALLBACK'] = '1'
sys.path.append('/mnt/shared/Projects/Metis')
from server.database.connection import async_session_factory
from server.repositories.job_repository import JobRepository
from sqlalchemy import select
from server.database.models import User

async def test():
    async with async_session_factory() as db:
        user = (await db.execute(select(User).where(User.email == 'abhi@gmail.com'))).scalar()
        repo = JobRepository(db)
        stats = await repo.get_user_stats(str(user.id))
        print("Stats for abhi@gmail.com:", stats)

asyncio.run(test())
