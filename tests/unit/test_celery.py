import asyncio
import uuid
import os
from server.database.connection import async_session_factory
from server.repositories.job_repository import JobRepository
from microservices.tasks import process_file_task

async def main():
    async with async_session_factory() as db:
        job_repo = JobRepository(db)
        # Create a mock job
        job = await job_repo.create(
            user_id=str(uuid.uuid4()),
            file_name="test.txt",
            file_type="text/plain",
            file_size_bytes=100
        )
        job_id = str(job.id)
        
        # Create a mock file
        file_path = f"uploads/test_{job_id}.txt"
        os.makedirs("uploads", exist_ok=True)
        with open(file_path, "w") as f:
            f.write("My name is John Doe and my email is john.doe@example.com.")
            
        print(f"Created job {job_id} and file {file_path}")
        
        # Dispatch to celery
        print("Dispatching task...")
        result = process_file_task.delay(job_id, file_path, "test.txt")
        print(f"Task dispatched with id {result.id}")
        
        # Wait for completion
        print("Waiting for result...")
        res = result.get(timeout=30)
        print(f"Result: {res}")
        
if __name__ == "__main__":
    asyncio.run(main())
