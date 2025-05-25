from pydantic import BaseModel, EmailStr

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
    description: str | None = None  # Опциональное поле
    rating: float | None = None    # Опциональное поле

class HotelCreate(HotelBase):
    pass

class HotelResponse(HotelBase):
    id: int
    owner_id: int

    class Config:
        from_attributes = True