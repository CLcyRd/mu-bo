from concurrent.futures import ThreadPoolExecutor
import os
import sys
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import auth, models
from app.database import Base
from app.routers import volunteers as volunteers_router


def build_payload(user_id: int, **overrides):
    data = {
        "user_id": user_id,
        "name": "测试用户",
        "gender": "女",
        "id_card": "310101199001011234",
        "age": 28,
        "ethnicity": "汉族",
        "phone": "13800138000",
        "service_time": "周三、周六",
        "organization": "上海电影学院",
        "position": "学生",
        "email": "test@example.com",
        "note": "测试备注",
    }
    data.update(overrides)
    return data


def build_test_client():
    engine = create_engine("sqlite:///./test_volunteers_unit.db", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    app = FastAPI()
    app.include_router(volunteers_router.router)

    def get_test_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def fake_admin():
        return models.User(id=999, username="admin", role="admin", is_active=True)

    app.dependency_overrides[volunteers_router.database.get_db] = get_test_db
    app.dependency_overrides[auth.get_current_admin_user] = fake_admin
    client = TestClient(app)
    return client, TestingSessionLocal


def seed_user(session_local, user_id: int):
    db = session_local()
    try:
        user = models.User(id=user_id, username=f"user_{user_id}", role="user", is_active=True)
        db.add(user)
        db.commit()
    finally:
        db.close()


def test_register_validation_error():
    client, session_local = build_test_client()
    seed_user(session_local, 101)
    response = client.post(
        "/volunteers/register",
        json=build_payload(101, name="张三", phone="13x00000000", email="badmail", note="n"),
    )
    assert response.status_code == 400
    payload = response.json()
    assert payload["code"] == 4001
    assert len(payload["data"]["fields"]) >= 1


def test_register_idempotent():
    client, session_local = build_test_client()
    seed_user(session_local, 102)
    body = build_payload(102, name="李四", email="li@example.com", note="hello")
    first = client.post("/volunteers/register", json=body)
    second = client.post("/volunteers/register", json=body)

    assert first.status_code == 200
    assert second.status_code == 200
    assert first.json()["data"]["volunteer_id"] == second.json()["data"]["volunteer_id"]
    assert second.json()["data"]["existed"] is True

    db = session_local()
    try:
        count = db.query(models.Volunteer).filter(models.Volunteer.user_id == 102).count()
        assert count == 1
    finally:
        db.close()


def test_register_rollback_on_exception():
    client, session_local = build_test_client()
    seed_user(session_local, 103)

    def trigger_fail(session, *_):
        for item in session.new:
            if isinstance(item, models.Volunteer) and item.note == "ROLLBACK":
                raise RuntimeError("force rollback")

    event.listen(session_local, "before_flush", trigger_fail)
    try:
        response = client.post(
            "/volunteers/register",
            json=build_payload(103, name="王五", phone="13900139000", email="w@example.com", note="ROLLBACK"),
        )
        assert response.status_code == 500
    finally:
        event.remove(session_local, "before_flush", trigger_fail)

    db = session_local()
    try:
        count = db.query(models.Volunteer).filter(models.Volunteer.user_id == 103).count()
        assert count == 0
    finally:
        db.close()


def test_patch_status_admin_only_route_logic():
    client, session_local = build_test_client()
    seed_user(session_local, 104)
    create = client.post(
        "/volunteers/register",
        json=build_payload(104, name="赵六", phone="13700137000", email="zhao@example.com", note="note"),
    )
    volunteer_id = create.json()["data"]["volunteer_id"]
    update = client.patch(f"/volunteers/{volunteer_id}/status", json={"status": "已审核"})
    assert update.status_code == 200
    assert update.json()["data"]["status"] == "已审核"


def test_update_note_route_logic():
    client, session_local = build_test_client()
    seed_user(session_local, 107)
    create = client.post(
        "/volunteers/register",
        json=build_payload(107, name="周八", phone="13400134000", email="zhou@example.com", note="old"),
    )
    volunteer_id = create.json()["data"]["volunteer_id"]
    update = client.patch(f"/volunteers/{volunteer_id}/note", json={"note": "new note"})
    assert update.status_code == 200
    assert update.json()["data"]["note"] == "new note"

    db = session_local()
    try:
        row = db.query(models.Volunteer).filter(models.Volunteer.volunteer_id == volunteer_id).first()
        assert row is not None
        assert row.note == "new note"
    finally:
        db.close()


def test_delete_volunteer_route_logic():
    client, session_local = build_test_client()
    seed_user(session_local, 106)
    create = client.post(
        "/volunteers/register",
        json=build_payload(106, name="孙七", phone="13500135000", email="sun@example.com", note="note"),
    )
    volunteer_id = create.json()["data"]["volunteer_id"]
    remove = client.delete(f"/volunteers/{volunteer_id}")
    assert remove.status_code == 200
    assert remove.json()["data"]["volunteer_id"] == volunteer_id

    db = session_local()
    try:
        count = db.query(models.Volunteer).filter(models.Volunteer.volunteer_id == volunteer_id).count()
        assert count == 0
    finally:
        db.close()


def test_register_concurrent_idempotent():
    client, session_local = build_test_client()
    volunteers_router._RATE_LIMIT_COUNT = 1000
    seed_user(session_local, 105)
    payload = build_payload(105, name="并发用户", phone="13600136000", email="cc@example.com", note="n")

    def submit():
        return client.post("/volunteers/register", json=payload)

    with ThreadPoolExecutor(max_workers=20) as pool:
        responses = [f.result() for f in [pool.submit(submit) for _ in range(50)]]

    assert all(item.status_code == 200 for item in responses)
    ids = {item.json()["data"]["volunteer_id"] for item in responses}
    assert len(ids) == 1
