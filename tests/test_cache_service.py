
import pytest
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.db.models import Base
from app.services.cache_service import CacheService


@pytest.fixture
async def session():
    engine = create_async_engine(
        "sqlite+aiosqlite://",
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    Session = async_sessionmaker(bind=engine, expire_on_commit=False)
    async with Session() as s:
        yield s
    await engine.dispose()


async def test_cache_set_and_get(session):
    service = CacheService()
    await service.set(session, "ns", {"a": 1, "b": 2}, {"data": [1, 2, 3]}, expire_minutes=60)
    result = await service.get(session, "ns", {"b": 2, "a": 1})
    assert result == {"data": [1, 2, 3]}


async def test_cache_miss_returns_none(session):
    service = CacheService()
    assert await service.get(session, "ns", {"a": 1}) is None


async def test_cache_expired_returns_none(session):
    service = CacheService()
    await service.set(session, "ns", {"a": 1}, {"data": 42}, expire_minutes=-5)
    assert await service.get(session, "ns", {"a": 1}) is None


async def test_cache_hash_is_stable_and_namespaced(session):
    service = CacheService()
    h1 = service._generate_hash("ns1", {"x": 1, "y": 2})
    h2 = service._generate_hash("ns1", {"y": 2, "x": 1})
    h3 = service._generate_hash("ns2", {"x": 1, "y": 2})
    assert h1 == h2
    assert h1 != h3


async def test_cache_upsert_overwrites(session):
    service = CacheService()
    await service.set(session, "ns", {"a": 1}, {"v": 1}, expire_minutes=60)
    await service.set(session, "ns", {"a": 1}, {"v": 2}, expire_minutes=60)
    assert await service.get(session, "ns", {"a": 1}) == {"v": 2}
