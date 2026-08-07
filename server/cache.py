import hashlib
import json
import os
import redis.asyncio as aioredis
from typing import Optional, Dict, Any

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")

class CacheService:
    def __init__(self):
        self.redis = None
        
    async def connect(self):
        if not self.redis:
            self.redis = aioredis.from_url(REDIS_URL, decode_responses=True)
            
    async def disconnect(self):
        if self.redis:
            await self.redis.close()
            
    def compute_hash(self, file_content: bytes) -> str:
        """Compute SHA-256 hash of file content"""
        return hashlib.sha256(file_content).hexdigest()
        
    async def get_cached_result(self, file_hash: str) -> Optional[Dict[str, Any]]:
        """Check if result exists in cache"""
        if not self.redis:
            await self.connect()
        try:
            cached = await self.redis.get(f"metis:result:{file_hash}")
            if cached:
                return json.loads(cached)
        except Exception as e:
            print(f"Redis cache GET error: {e}")
        return None
        
    async def set_cached_result(self, file_hash: str, result: Dict[str, Any], ttl_seconds: int = 3600):
        """Save result to cache with TTL (default 1 hour)"""
        if not self.redis:
            await self.connect()
        try:
            await self.redis.setex(
                f"metis:result:{file_hash}",
                ttl_seconds,
                json.dumps(result)
            )
        except Exception as e:
            print(f"Redis cache SET error: {e}")

# Singleton instance
cache_service = CacheService()
