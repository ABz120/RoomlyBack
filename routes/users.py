from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from schemas import UserCreate, UserResponse
from models import User
from database import get_db
from utils import hash_password, verify_password, create_access_token, get_current_user

router = APIRouter()

class UserLogin(BaseModel):
    email: str
    password: str

@router.post("/register", response_model=UserResponse)
async def create_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    # Проверяем, есть ли уже пользователь с таким email
    result = await db.execute(select(User).filter(User.email == user.email))
    db_user = result.scalar_one_or_none()
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    if user.role not in ["regular", "business"]:
        raise HTTPException(status_code=400, detail="Invalid role")

    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, hashed_password=hashed_password, role=user.role)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user

@router.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).filter(User.email == user.email))
    db_user = result.scalar_one_or_none()

    if not db_user or not verify_password(user.password, db_user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(data={"sub": db_user.email})

    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
