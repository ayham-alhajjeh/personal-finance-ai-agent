from fastapi import APIRouter # type: ignore

router = APIRouter()

@router.get("/")
def root():
    return {"message": "Hello from FastAPI (via router)"}
