from pydantic import BaseModel, EmailStr
from datetime import datetime


class UserBase(BaseModel):
    email: EmailStr
    role: str  # "regular" или "business"


class UserCreate(UserBase):
    password: str


class UserResponse(UserBase):
    id: int

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class HotelBase(BaseModel):
    name: str
    address: str
    description: str | None = None
    rating: float | None = None


class HotelCreate(HotelBase):
    pass


class HotelResponse(HotelBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True


class RoomBase(BaseModel):
    room_number: str
    room_type: str


class RoomCreate(RoomBase):
    hotel_id: int


class RoomResponse(RoomBase):
    id: int
    hotel_id: int

    class Config:
        from_attributes = True


class RoomOfferBase(BaseModel):
    start_date: datetime
    end_date: datetime
    initial_price: float
    min_price: float
    available: int = 1


class RoomOfferCreate(RoomOfferBase):
    room_id: int


class RoomOfferResponse(RoomOfferBase):
    id: int
    room_id: int
    current_price: float
    popularity_factor: float
    created_at: datetime

    class Config:
        from_attributes = True
