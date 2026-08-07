import os
os.environ['SQLITE_FALLBACK'] = '1'

import asyncio
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from server.database.models import User
from server.auth import hash_password
from server.config import settings

async def reset_password(email: str, new_password: str):
    engine = create_async_engine(settings.DATABASE_URL)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        from sqlalchemy.future import select
        result = await session.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if user:
            user.password_hash = hash_password(new_password)
            await session.commit()
            print(f"Successfully updated password for {email}")
        else:
            print(f"User not found: {email}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 3:
        print("Usage: python reset_password.py <email> <new_password>")
        sys.exit(1)
    
    asyncio.run(reset_password(sys.argv[1], sys.argv[2]))
