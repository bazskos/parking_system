from fastapi import FastAPI, Depends, HTTPException
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

@app.post("/bookings", response_model=schemas.BookingResponse)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    
    # 1. Alapvető validáció: a vége nem lehet a kezdete előtt
    if booking.end_time <= booking.start_time:
        raise HTTPException(status_code=400, detail="A záró időpontnak a kezdő időpont után kell lennie.")

    # 2. Ellenőrizzük, hogy létezik-e a kért parkolóhely
    spot = db.query(models.ParkingSpot).filter(models.ParkingSpot.id == booking.parking_spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="A megadott parkolóhely nem létezik.")

    # 3. Overlap logic
    overlapping_booking = db.query(models.Booking).filter(
        models.Booking.parking_spot_id == booking.parking_spot_id,
        models.Booking.start_time < booking.end_time,
        models.Booking.end_time > booking.start_time
    ).first()

    if overlapping_booking:
        raise HTTPException(status_code=400, detail="A parkolóhely ebben az időszakban már foglalt.")

    # 4. Ha minden rendben, elmentjük az új foglalást
    new_booking = models.Booking(
        parking_spot_id=booking.parking_spot_id,
        applicant_name=booking.applicant_name,
        start_time=booking.start_time,
        end_time=booking.end_time
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return new_booking


# Egy adott parkolóhely foglalásainak lekérdezése
@app.get("/spots/{spot_id}/bookings", response_model=List[schemas.BookingResponse])
def get_bookings_for_spot(spot_id: int, db: Session = Depends(get_db)):
    # 1. Ellenőrizzük, hogy létezik-e egyáltalán a kért parkolóhely
    spot = db.query(models.ParkingSpot).filter(models.ParkingSpot.id == spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="A megadott parkolóhely nem létezik.")
    
    # 2. Lekérjük a helyhez tartozó összes foglalást
    bookings = db.query(models.Booking).filter(models.Booking.parking_spot_id == spot_id).all()
    return bookings


# Foglalás lemondása
@app.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    # 1. Megkeressük a foglalást
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="A foglalás nem található.")
    
    # 2. Töröljük az adatbázisból
    db.delete(booking)
    db.commit()
    
    return {"message": "A foglalás sikeresen törölve.", "deleted_booking_id": booking_id}