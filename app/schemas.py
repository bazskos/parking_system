from pydantic import BaseModel
from datetime import datetime

class ParkingSpotBase(BaseModel):
    name: str
    type: str

class ParkingSpotResponse(ParkingSpotBase):
    id: int

    class Config:
        from_attributes = True

class BookingCreate(BaseModel):
    parking_spot_id: int
    applicant_name: str
    start_time: datetime
    end_time: datetime
    has_vip_pass: bool = False
    has_disabled_badge: bool = False

class BookingResponse(BookingCreate):
    id: int

    class Config:
        from_attributes = True