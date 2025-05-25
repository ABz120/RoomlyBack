from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_business():
    return {"message": "Business endpoint"}