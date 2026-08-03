import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app, get_db
from app.database import Base
from app.models import ParkingSpot

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    
    db.add(ParkingSpot(id=1, name="T-01", type="normal"))
    db.add(ParkingSpot(id=2, name="TVIP-01", type="vip"))
    db.commit()
    db.close()


def test_get_spots():
    response = client.get("/spots")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "T-01"

def test_create_booking_success():
    response = client.post("/bookings", json={
        "parking_spot_id": 1,
        "applicant_name": "Teszt Elek",
        "start_time": "2026-08-10T10:00:00",
        "end_time": "2026-08-10T12:00:00",
        "has_vip_pass": False,
        "has_disabled_badge": False
    })
    assert response.status_code == 200
    assert response.json()["applicant_name"] == "Teszt Elek"

def test_create_booking_overlap():
    client.post("/bookings", json={
        "parking_spot_id": 1,
        "applicant_name": "Teszt Elek",
        "start_time": "2026-08-10T10:00:00",
        "end_time": "2026-08-10T12:00:00"
    })
    
    response = client.post("/bookings", json={
        "parking_spot_id": 1,
        "applicant_name": "Másik Ember",
        "start_time": "2026-08-10T11:00:00",
        "end_time": "2026-08-10T13:00:00"
    })
    assert response.status_code == 400
    assert "foglalt" in response.json()["detail"]

def test_vip_booking_forbidden():
    response = client.post("/bookings", json={
        "parking_spot_id": 2,
        "applicant_name": "Jogosulatlan Jani",
        "start_time": "2026-08-10T10:00:00",
        "end_time": "2026-08-10T12:00:00",
        "has_vip_pass": False
    })
    assert response.status_code == 403