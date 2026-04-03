"""
pytest configuration and fixtures
پیکربندی تست‌ها و فیکسچرها
"""

import asyncio
import io

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.database import Base, get_db
from app.main import app


# ---------------------------------------------------------------------------
# Event loop (pytest-asyncio >= 0.21 compatible)
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ---------------------------------------------------------------------------
# In-memory async SQLite engine for tests
# ---------------------------------------------------------------------------

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

_test_engine = create_async_engine(TEST_DATABASE_URL, echo=False)
_TestSessionLocal = async_sessionmaker(
    _test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest_asyncio.fixture(scope="function")
async def async_db():
    """Provide a fresh in-memory async database session per test"""
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with _TestSessionLocal() as session:
        yield session
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# ---------------------------------------------------------------------------
# Override DB dependency so TestClient uses in-memory SQLite
# ---------------------------------------------------------------------------

async def _override_get_db():
    async with _TestSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = _override_get_db


@pytest.fixture(scope="session")
async def _setup_test_db():
    """
    Creates schema once per test session.
    The `async_db` fixture (function-scoped) independently creates/drops per test
    using the same in-memory engine so both fixtures coexist safely.
    """
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with _test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def client(_setup_test_db):
    """TestClient fixture backed by in-memory database"""
    with TestClient(app, raise_server_exceptions=True) as c:
        yield c


# ---------------------------------------------------------------------------
# Minimal test image fixture (1×1 white PNG in bytes)
# ---------------------------------------------------------------------------

@pytest.fixture()
def test_plate_image() -> bytes:
    """Returns valid 1-pixel PNG bytes for upload testing"""
    try:
        from PIL import Image

        buf = io.BytesIO()
        img = Image.new("RGB", (100, 50), color=(255, 255, 255))
        img.save(buf, format="PNG")
        return buf.getvalue()
    except ImportError:
        # Minimal valid PNG (1×1 white pixel)
        return (
            b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01"
            b"\x00\x00\x00\x01\x08\x02\x00\x00\x00\x90wS\xde\x00\x00"
            b"\x00\x0cIDATx\x9cc\xf8\xff\xff?\x00\x05\xfe\x02\xfe\xdc"
            b"\xccY\xe7\x00\x00\x00\x00IEND\xaeB`\x82"
        )
