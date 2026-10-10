import os
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.database import Base, get_db
from app.main import app
from app.seed.seed_data import run_seed

# Use an in-memory SQLite database for testing isolation
TEST_DATABASE_URL = "sqlite:///./test_tenantai.db"
test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    db = TestingSessionLocal()
    run_seed(db)
    yield
    db.close()
    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists("./test_tenantai.db"):
        try:
            os.remove("./test_tenantai.db")
        except Exception:
            pass


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def technova_admin_token(client):
    resp = client.post("/api/v1/auth/login", json={
        "email": "admin@technova.com",
        "password": "DemoPass123!"
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture
def technova_user_token(client):
    resp = client.post("/api/v1/auth/login", json={
        "email": "user@technova.com",
        "password": "DemoPass123!"
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture
def greenleaf_admin_token(client):
    resp = client.post("/api/v1/auth/login", json={
        "email": "admin@greenleaf.com",
        "password": "DemoPass123!"
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture
def greenleaf_user_token(client):
    resp = client.post("/api/v1/auth/login", json={
        "email": "user@greenleaf.com",
        "password": "DemoPass123!"
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]


@pytest.fixture
def superadmin_token(client):
    resp = client.post("/api/v1/auth/login", json={
        "email": "admin@tenantai.com",
        "password": "SuperAdmin123!"
    })
    assert resp.status_code == 200
    return resp.json()["access_token"]
