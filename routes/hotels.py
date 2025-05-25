from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import HotelCreate, HotelResponse
from models import Hotel, User
from database import get_db
from utils import get_current_user

router = APIRouter()

@router.post("/", response_model=HotelResponse)
def create_hotel(hotel: HotelCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "business":
        raise HTTPException(status_code=403, detail="Only business users can create hotels")
    new_hotel = Hotel(name=hotel.name, address=hotel.address, description=hotel.description, rating=hotel.rating, owner_id=current_user.id)
    db.add(new_hotel)
    db.commit()
    db.refresh(new_hotel)
    return new_hotel

@router.get("/", response_model=list[HotelResponse])
def get_hotels(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    hotels = db.query(Hotel).all()
    return hotels