from sqlalchemy import Column, Integer, String, ForeignKey, Float
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # "regular" или "business"

class Hotel(Base):
    __tablename__ = "hotels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    description = Column(String, nullable=True)  # Описание отеля (опционально)
    rating = Column(Float, nullable=True)       # Рейтинг отеля (опционально)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="hotels")

# связь для User
User.hotels = relationship("Hotel", back_populates="owner")