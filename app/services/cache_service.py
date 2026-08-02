from datetime import datetime, timedelta
import hashlib
import json
from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.dialects.sqlite import insert

from app.db.models import APIQueryCacheModel

class CacheService:
    def _generate_hash(self, namespace: str, params: dict) -> str:
        sorted_str = json.dumps(params, sort_keys=True)
        raw_key = f"{namespace}:{sorted_str}"
        return hashlib.md5(raw_key.encode("utf-8")).hexdigest()

    async def get(self, session: AsyncSession, namespace: str, params: dict) -> Optional[Any]:
        q_hash = self._generate_hash(namespace, params)
        stmt = select(APIQueryCacheModel).where(APIQueryCacheModel.query_hash == q_hash)
        result = await session.execute(stmt)
        cache_entry = result.scalars().first()

        if cache_entry:
            if cache_entry.expires_at > datetime.utcnow():
                return cache_entry.response_data
            else:
                pass
        return None

    async def set(
        self, session: AsyncSession, namespace: str, params: dict, data: Any, expire_minutes: int = 10080
    ) -> None:
        q_hash = self._generate_hash(namespace, params)
        expires_at = datetime.utcnow() + timedelta(minutes=expire_minutes)

        stmt = insert(APIQueryCacheModel).values(
            query_hash=q_hash,
            response_data=data,
            expires_at=expires_at,
            created_at=datetime.utcnow()
        )
        stmt = stmt.on_conflict_do_update(
            index_elements=['query_hash'], 
            set_={
                "response_data": data,
                "expires_at": expires_at,
                "created_at": datetime.utcnow()
            }
        )
        await session.execute(stmt)
        await session.commit()

cache_service = CacheService()