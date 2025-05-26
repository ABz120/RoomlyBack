from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from models import Favorite, Room, User
from database import get_db
from utils import get_current_user

router = APIRouter()

@router.post("/favorites/{room_id}", status_code=201)
async def add_favorite(room_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Проверяем, существует ли номер
    result = await db.execute(select(Room).filter(Room.id == room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    # Проверяем, есть ли уже в избранном
    result = await db.execute(
        select(Favorite).filter(Favorite.user_id == current_user.id, Favorite.room_id == room_id)
    )
    existing = result.scalar_one_or_none()
    if existing:
        raise HTTPException(status_code=400, detail="Room already in favorites")

    favorite = Favorite(user_id=current_user.id, room_id=room_id)
    db.add(favorite)
    await db.commit()
    return {"detail": "Room added to favorites"}

@router.delete("/favorites/{room_id}", status_code=204)
async def remove_favorite(room_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Favorite).filter(Favorite.user_id == current_user.id, Favorite.room_id == room_id)
    )
    favorite = result.scalar_one_or_none()
    if not favorite:
        raise HTTPException(status_code=404, detail="Favorite not found")

    await db.delete(favorite)
    await db.commit()
    return

@router.get("/favorites/", response_model=list[int])  # или список моделей RoomResponse, если хочешь детали
async def get_favorites(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(
        select(Favorite).filter(Favorite.user_id == current_user.id)
    )
    favorites = result.scalars().all()
    return [fav.room_id for fav in favorites]
