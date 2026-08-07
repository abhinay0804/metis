import asyncio
import httpx
from server.database.connection import async_session_factory
from server.repositories.user_repository import UserRepository
from server.auth import create_access_token

async def main():
    # 1. Get user from DB
    async with async_session_factory() as session:
        repo = UserRepository(session)
        user = await repo.get_by_email('abhi@gmail.com')
        if not user:
            print("User not found!")
            return
        
        print(f"Found user: {user.id}")
        token = create_access_token(str(user.id), user.email)
        print(f"Generated token")

    # 2. Make API request
    async with httpx.AsyncClient() as client:
        headers = {"Authorization": f"Bearer {token}"}
        resp = await client.get("http://localhost:8001/user-metrics", headers=headers)
        print(f"Status: {resp.status_code}")
        print(f"Response: {resp.json()}")

if __name__ == "__main__":
    asyncio.run(main())
