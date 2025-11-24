from fastapi import FastAPI # type: ignore
from .routers import root

app = FastAPI()

app.include_router(root.router)
