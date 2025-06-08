from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy import select
from schemas import HotelCreate, HotelResponse, RoomCreate, RoomResponse, RoomOfferCreate, RoomOfferResponse
from models import Hotel, User, Room, RoomOffer
from database import get_db
from utils import get_current_user
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import math
import random

router = APIRouter()


@router.post("/", response_model=HotelResponse)
async def create_hotel(hotel: HotelCreate, db: AsyncSession = Depends(get_db),
                       current_user: User = Depends(get_current_user)):
    if current_user.role != "business":
        raise HTTPException(status_code=403, detail="Only business users can create hotels")
    new_hotel = Hotel(**hotel.dict(), owner_id=current_user.id)
    db.add(new_hotel)
    await db.commit()
    await db.refresh(new_hotel)
    return new_hotel


@router.post("/rooms/", response_model=RoomResponse)
async def create_room(room: RoomCreate, db: AsyncSession = Depends(get_db),
                      current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Hotel).filter(Hotel.id == room.hotel_id))
    hotel = result.scalar_one_or_none()
    if not hotel or hotel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only add rooms to your own hotels")
    new_room = Room(**room.dict())
    db.add(new_room)
    await db.commit()
    await db.refresh(new_room)
    return new_room


@router.post("/rooms/offers/", response_model=RoomOfferResponse)
async def create_room_offer(offer: RoomOfferCreate, db: AsyncSession = Depends(get_db),
                            current_user: User = Depends(get_current_user)):
    result = await db.execute(select(Room).filter(Room.id == offer.room_id))
    room = result.scalar_one_or_none()
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    result = await db.execute(select(Hotel).filter(Hotel.id == room.hotel_id))
    hotel = result.scalar_one_or_none()
    if hotel.owner_id != current_user.id:
        raise HTTPException(status_code=403, detail="You can only add offers to your own rooms")
    new_offer = RoomOffer(**offer.dict(), current_price=offer.initial_price, popularity_factor=1.0)
    db.add(new_offer)
    await db.commit()
    await db.refresh(new_offer)
    return new_offer


@router.get("/rooms/offers/", response_model=list[RoomOfferResponse])
async def get_room_offers(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    result = await db.execute(select(RoomOffer))
    offers = result.scalars().all()
    return offers


def calculate_dynamic_price(offer: RoomOffer) -> float:
    created_at = offer.created_at
    if created_at.tzinfo is None:
        created_at = created_at.replace(tzinfo=timezone.utc)
    time_elapsed_hours = (datetime.now(timezone.utc) - created_at).total_seconds() / 3600
    k = 0.2 * offer.popularity_factor
    base_price = offer.initial_price * math.exp(-k * time_elapsed_hours)
    noise = base_price * random.uniform(-0.01, 0.01)
    price = base_price + noise
    return max(price, offer.min_price)


@router.post("/rooms/offers/{offer_id}/book")
async def book_offer(
        offer_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    try:
        result = await db.execute(
            select(RoomOffer).filter(RoomOffer.id == offer_id).with_for_update()
        )
        offer = result.scalar_one_or_none()
        if not offer:
            raise HTTPException(status_code=404, detail="Offer not found")
        if offer.available <= 0:
            raise HTTPException(status_code=400, detail="Offer is no longer available")

        current_price = calculate_dynamic_price(offer)
        offer.available -= 1

        await db.commit()

        return {
            "offer_id": offer_id,
            "user_id": current_user.id,
            "booked_price": round(current_price, 2)
        }

    except HTTPException:
        raise  # не трогаем HTTP-ошибки

    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=str(e))


@router.websocket("/rooms/offers/{offer_id}")
async def websocket_price(websocket: WebSocket, offer_id: int, db: AsyncSession = Depends(get_db)):
    await websocket.accept()
    try:
        # Фиксация просмотра при подключении
        await record_offer_view(offer_id, db)
        while True:
            result = await db.execute(select(RoomOffer).filter(RoomOffer.id == offer_id))
            offer = result.scalar_one_or_none()
            if not offer:
                await websocket.send_json({"error": "Offer not found"})
                break
            current_price = calculate_dynamic_price(offer)
            await websocket.send_json({"offer_id": offer_id, "current_price": round(current_price, 2)})
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await websocket.close(code=1000, reason=str(e))


async def record_offer_view(offer_id: int, db: AsyncSession):
    await db.execute(
        """
        INSERT INTO offer_views (offer_id, timestamp)
        VALUES (:offer_id, :timestamp)
        """,
        {"offer_id": offer_id, "timestamp": datetime.now(timezone.utc)}
    )
    await db.commit()


@router.post("/rooms/offers/{offer_id}/view", status_code=200)
async def record_offer_view(offer_id: int, db: AsyncSession = Depends(get_db)):
    # Проверяем существование предложения
    result = await db.execute(select(RoomOffer).filter(RoomOffer.id == offer_id))
    offer = result.scalar_one_or_none()
    if not offer:
        raise HTTPException(status_code=404, detail="Offer not found")

    # Фиксация просмотра
    await db.execute(
        """
        INSERT INTO offer_views (offer_id, timestamp)
        VALUES (:offer_id, :timestamp)
        """,
        {"offer_id": offer_id, "timestamp": datetime.now(timezone.utc)}
    )
    await db.commit()
    return {"detail": "View recorded", "offer_id": offer_id}
