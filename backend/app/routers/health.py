from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def health():
    return {"message": "Aziz AI Pro backend working ✔️"}
