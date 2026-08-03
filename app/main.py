from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from typing import List

from .database import engine, SessionLocal
from . import models, schemas

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Parkolóhely-foglalás API",
    description="Backend szolgáltatás parkolóhelyek kezeléséhez és foglalásához.",
    version="1.0.0"
)

def init_db():
    db = SessionLocal()
    try:
        if db.query(models.ParkingSpot).count() == 0:
            alap_helyek = [
                models.ParkingSpot(name="P-01", type="normal"),
                models.ParkingSpot(name="P-02", type="normal"),
                models.ParkingSpot(name="P-03", type="normal"),
                models.ParkingSpot(name="VIP-01", type="vip"),
                models.ParkingSpot(name="DIS-01", type="disabled"),
            ]
            db.add_all(alap_helyek)
            db.commit()
            print("Adatbázis sikeresen feltöltve alap adatokkal!")
    finally:
        db.close()

init_db()

# Adatbázis session függőség
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/")
def health_check():
    return {"status": "ok", "message": "A Parkolóhely-foglalás API fut és az adatbázis inicializálva!"}

@app.get("/spots", response_model=List[schemas.ParkingSpotResponse])
def get_parking_spots(db: Session = Depends(get_db)):
    spots = db.query(models.ParkingSpot).all()
    return spots