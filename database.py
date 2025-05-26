# database.py

import os
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import asynccontextmanager

# Загружаем переменные окружения из .env
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("DATABASE_URL не найден в .env файле")

# Создаём асинхронный движок SQLAlchemy
engine = create_async_engine(DATABASE_URL, echo=True)

# Фабрика для создания асинхронных сессий
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Асинхронный контекстный менеджер — удобно использовать в FastAPI Depends
@asynccontextmanager
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# Удобная функция для получения сессии вручную (например, в фоновом таске)
async def get_db_session() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        return session

# Базовый класс моделей
Base = declarative_base()
