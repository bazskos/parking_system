from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
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
    has_vip_pass = Column(Boolean, default=False)
    has_disabled_badge = Column(Boolean, default=False)
    spot = relationship("ParkingSpot", back_populates="bookings")