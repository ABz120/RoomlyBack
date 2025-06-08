import math
from datetime import datetime, timezone, timedelta
from fastapi import FastAPI
from routes import users, hotels, favorites
from database import Base, engine, get_db_session
from models import RoomOffer
from sqlalchemy import select, update
from contextlib import asynccontextmanager
from celery import Celery
from celery.schedules import crontab

# Создание таблиц при запуске
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Функция расчета динамической цены (предполагается в routes.hotels)
# from routes.hotels import calculate_dynamic_price  # Убедитесь, что она импортируется

# Фоновая задача по обновлению цен и популярности
async def update_offer_data():
    async with get_db_session() as db:
        result = await db.execute(select(RoomOffer))
        offers = result.scalars().all()
        for offer in offers:
            # Обновление popularity_factor
            twelve_hours_ago = datetime.now(timezone.utc) - timedelta(hours=12)
            view_result = await db.execute(
                """
                SELECT COUNT(*) FROM offer_views
                WHERE offer_id = :offer_id AND timestamp >= :since
                """,
                {"offer_id": offer.id, "since": twelve_hours_ago}
            )
            view_count = view_result.scalar()
            new_popularity = min(math.log(view_count + 1), 5.0)
            if new_popularity != offer.popularity_factor:
                await db.execute(
                    update(RoomOffer)
                    .where(RoomOffer.id == offer.id)
                    .values(popularity_factor=new_popularity)
                )

            # Обновление current_price
            current_price = calculate_dynamic_price(offer)
            if current_price != offer.current_price:
                await db.execute(
                    update(RoomOffer)
                    .where(RoomOffer.id == offer.id)
                    .values(current_price=current_price)
                )
        await db.commit()

# Настройка Celery
celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",  # Используйте актуальный URL Redis
    backend="redis://redis:6379/0"
)
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)

# Регистрация задачи Celery
@celery_app.task
async def update_all_offers():
    await update_offer_data()

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    # Настройка Celery Beat
    celery_app.conf.beat_schedule = {
        "update-offers": {
            "task": "app.main.update_all_offers",
            "schedule": crontab(minute="*/1"),  # Каждую минуту для тестирования, можно изменить на 5
        },
    }
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(users.router, prefix="/api/users")
app.include_router(hotels.router, prefix="/api/hotels")
app.include_router(favorites.router, prefix="/api/favorites")

@app.get("/")
async def read_root():
    return {"message": "Welcome to the Hotel Booking API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)