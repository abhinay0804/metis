import asyncio
from server.database.connection import async_session_factory
from server.repositories.job_repository import JobRepository
from uuid import UUID

async def main():
    async with async_session_factory() as session:
        repo = JobRepository(session)
        dev_user_id = "93a00f1de3cc4e9d90e32f4ba490263f"
        
        # Test list
        jobs = await repo.list_by_user(dev_user_id)
        print(f"Jobs found: {len(jobs)}")
        
        # Test stats
        stats = await repo.get_user_stats(dev_user_id)
        print(f"Stats: {stats}")

if __name__ == "__main__":
    asyncio.run(main())
