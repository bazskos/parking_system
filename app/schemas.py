from pydantic import BaseModel

class ParkingSpotBase(BaseModel):
    name: str
    type: str

class ParkingSpotResponse(ParkingSpotBase):
    id: int

    class Config:
        from_attributes = True