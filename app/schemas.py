from datetime import date, datetime
from pydantic import BaseModel, ConfigDict, EmailStr, Field

class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(min_length=6, max_length=100)

class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    email: EmailStr
    role: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TrainCreate(BaseModel):
    train_number: str = Field(min_length=3, max_length=20)
    name: str = Field(min_length=2, max_length=120)
    source: str = Field(min_length=2, max_length=100)
    destination: str = Field(min_length=2, max_length=100)
    departure_time: str
    arrival_time: str
    travel_date: date

class TrainResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    train_number: str
    name: str
    source: str
    destination: str
    departure_time: str
    arrival_time: str
    travel_date: date
    is_active: bool

class SeatResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    coach: str
    seat_number: str
    seat_class: str
    fare: float
    is_available: bool

class BookingCreate(BaseModel):
    train_id: int
    seat_id: int
    passenger_name: str = Field(min_length=2, max_length=100)
    passenger_age: int = Field(ge=1, le=120)
    passenger_gender: str = Field(min_length=1, max_length=20)

class BookingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    pnr: str
    passenger_name: str
    passenger_age: int
    passenger_gender: str
    status: str
    amount: float
    booked_at: datetime
    train: TrainResponse
    seat: SeatResponse
