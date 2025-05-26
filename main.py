from fastapi import FastAPI
from routes import users, hotels
from database import Base, engine, get_db_session
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from models import RoomOffer
from sqlalchemy import select
from contextlib import asynccontextmanager
from routes.hotels import calculate_dynamic_price

# Создание таблиц при запуске
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Фоновая задача по обновлению цен
async def update_prices():
    db = await get_db_session()  # Удобная функция вместо async for
    result = await db.execute(select(RoomOffer))
    offers = result.scalars().all()
    for offer in offers:
        offer.current_price = calculate_dynamic_price(offer)
    await db.commit()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    scheduler = AsyncIOScheduler()
    scheduler.add_job(update_prices, "interval", seconds=10)
    scheduler.start()
    yield
    scheduler.shutdown()

app = FastAPI(lifespan=lifespan)

app.include_router(users.router, prefix="/api/users")
app.include_router(hotels.router, prefix="/api/hotels")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Hotel Booking API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
