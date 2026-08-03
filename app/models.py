from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

class ParkingSpot(Base):
    __tablename__ = "parking_spots"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    type = Column(String, default="normal")  # pl. "normal", "vip", "disabled"
    bookings = relationship("Booking", back_populates="spot")

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    parking_spot_id = Column(Integer, ForeignKey("parking_spots.id"))
    applicant_name = Column(String, index=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    spot = relationship("ParkingSpot", back_populates="bookings")