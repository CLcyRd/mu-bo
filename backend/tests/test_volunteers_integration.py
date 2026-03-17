import os
from concurrent.futures import ThreadPoolExecutor
import pytest
import sys
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import auth, models
from app.database import Base
from app.routers import volunteers as volunteers_router


@pytest.mark.integration
def test_mysql_testcontainer_concurrent_register_100_threads():
    mysql_module = pytest.importorskip("testcontainers.mysql")
    MySqlContainer = mysql_module.MySqlContainer
    if os.getenv("SKIP_TESTCONTAINERS") == "1":
        pytest.skip("skip by env")

    volunteers_router._RATE_LIMIT_COUNT = 1000
    with MySqlContainer("mysql:8.0.36") as mysql:
        db_url = mysql.get_connection_url().replace("mysql://", "mysql+pymysql://")
        engine = create_engine(db_url, pool_pre_ping=True)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        Base.metadata.create_all(bind=engine)

        db = SessionLocal()
        try:
            db.add(models.User(id=3001, username="integration_user", role="user", is_active=True))
            db.commit()
        finally:
            db.close()

        app = FastAPI()
        app.include_router(volunteers_router.router)

        def get_test_db():
            session = SessionLocal()
            try:
                yield session
            finally:
                session.close()

        def fake_admin():
            return models.User(id=1, username="admin", role="admin", is_active=True)

        app.dependency_overrides[volunteers_router.database.get_db] = get_test_db
        app.dependency_overrides[auth.get_current_admin_user] = fake_admin
        client = TestClient(app)

        payload = {
            "user_id": 3001,
            "name": "集成用户",
            "phone": "13500135000",
            "email": "integration@example.com",
            "note": "integration",
        }

        def submit():
            return client.post("/volunteers/register", json=payload)

        with ThreadPoolExecutor(max_workers=100) as pool:
            responses = [f.result() for f in [pool.submit(submit) for _ in range(100)]]

        assert all(r.status_code == 200 for r in responses)
        ids = {r.json()["data"]["volunteer_id"] for r in responses}
        assert len(ids) == 1

        db = SessionLocal()
        try:
            rows = db.query(models.Volunteer).filter(models.Volunteer.user_id == 3001).all()
            assert len(rows) == 1
        finally:
            db.close()
