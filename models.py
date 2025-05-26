from sqlalchemy import Column, Integer, String, ForeignKey, Float, DateTime
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime, UTC

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)  # "regular" или "business"
    hotels = relationship("Hotel", back_populates="owner")

class Hotel(Base):
    __tablename__ = "hotels"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    address = Column(String)
    description = Column(String, nullable=True)
    rating = Column(Float, nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="hotels")
    rooms = relationship("Room", back_populates="hotel")

class Room(Base):
    __tablename__ = "rooms"
    id = Column(Integer, primary_key=True, index=True)
    hotel_id = Column(Integer, ForeignKey("hotels.id"))
    room_number = Column(String, index=True)  # Номер комнаты (например, "101")
    room_type = Column(String)               # Тип комнаты (например, "single", "double")
    hotel = relationship("Hotel", back_populates="rooms")
    offers = relationship("RoomOffer", back_populates="room")

class RoomOffer(Base):
    __tablename__ = "room_offers"
    id = Column(Integer, primary_key=True, index=True)
    room_id = Column(Integer, ForeignKey("rooms.id"))
    start_date = Column(DateTime(timezone=True), nullable=False)  # Дата начала периода
    end_date = Column(DateTime(timezone=True), nullable=False)    # Дата окончания периода
    initial_price = Column(Float, nullable=False)  # Начальная цена за весь период
    current_price = Column(Float, nullable=False)  # Текущая цена (снижается со временем)
    min_price = Column(Float, nullable=False)      # Минимальная цена
    popularity_factor = Column(Float, default=1.0) # Коэффициент популярности
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(UTC))  # Время создания предложения
    available = Column(Integer, default=1)         # Количество доступных предложений
    room = relationship("Room", back_populates="offers")