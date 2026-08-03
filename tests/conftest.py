import os
import pathlib

# Point the app at an isolated test database BEFORE importing any app module.
TEST_DATA_DIR = pathlib.Path(__file__).resolve().parent.parent / "data"
TEST_DATA_DIR.mkdir(exist_ok=True)
TEST_DB = TEST_DATA_DIR / "test_trip_planner.db"
if TEST_DB.exists():
    TEST_DB.unlink()

os.environ["DATABASE_URL"] = f"sqlite+aiosqlite:///{TEST_DB}"
os.environ["SECRET_KEY"] = "test-secret-key-not-for-production"
