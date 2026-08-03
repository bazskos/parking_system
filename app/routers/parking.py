from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from .. import models, schemas
from ..database import get_db

router = APIRouter(tags=["Parking & Bookings"])

@router.get("/spots", response_model=List[schemas.ParkingSpotResponse])
def get_parking_spots(db: Session = Depends(get_db)):
    spots = db.query(models.ParkingSpot).all()
    return spots

@router.post("/bookings", response_model=schemas.BookingResponse)
def create_booking(booking: schemas.BookingCreate, db: Session = Depends(get_db)):
    if booking.end_time <= booking.start_time:
        raise HTTPException(status_code=400, detail="A záró időpontnak a kezdő időpont után kell lennie.")

    spot = db.query(models.ParkingSpot).filter(models.ParkingSpot.id == booking.parking_spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="A megadott parkolóhely nem létezik.")

    if spot.type == "vip" and not booking.has_vip_pass:
        raise HTTPException(status_code=403, detail="Ez egy VIP parkolóhely, nincs hozzá jogosultságod.")
    
    if spot.type == "disabled" and not booking.has_disabled_badge:
        raise HTTPException(status_code=403, detail="Ez a parkolóhely mozgáskorlátozottak számára van fenntartva.")

    overlapping_booking = db.query(models.Booking).filter(
        models.Booking.parking_spot_id == booking.parking_spot_id,
        models.Booking.start_time < booking.end_time,
        models.Booking.end_time > booking.start_time
    ).first()

    if overlapping_booking:
        raise HTTPException(status_code=400, detail="A parkolóhely ebben az időszakban már foglalt.")

    new_booking = models.Booking(
        parking_spot_id=booking.parking_spot_id,
        applicant_name=booking.applicant_name,
        start_time=booking.start_time,
        end_time=booking.end_time,
        has_vip_pass=booking.has_vip_pass,
        has_disabled_badge=booking.has_disabled_badge
    )
    
    db.add(new_booking)
    db.commit()
    db.refresh(new_booking)
    
    return new_booking

@router.get("/spots/{spot_id}/bookings", response_model=List[schemas.BookingResponse])
def get_bookings_for_spot(spot_id: int, db: Session = Depends(get_db)):
    spot = db.query(models.ParkingSpot).filter(models.ParkingSpot.id == spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="A megadott parkolóhely nem létezik.")
    
    bookings = db.query(models.Booking).filter(models.Booking.parking_spot_id == spot_id).all()
    return bookings

@router.delete("/bookings/{booking_id}")
def cancel_booking(booking_id: int, db: Session = Depends(get_db)):
    booking = db.query(models.Booking).filter(models.Booking.id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="A foglalás nem található.")
    
    db.delete(booking)
    db.commit()
    
    return {"message": "A foglalás sikeresen törölve.", "deleted_booking_id": booking_id}