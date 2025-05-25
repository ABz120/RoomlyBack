from fastapi import FastAPI
from routes import users, hotels
from database import Base, engine

# Создание таблиц при запуске
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(users.router, prefix="/api/users")
app.include_router(hotels.router, prefix="/api/hotels")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Hotel Booking API"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)