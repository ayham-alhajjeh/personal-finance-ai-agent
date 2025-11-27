from fastapi import FastAPI
from .routers import root
from .db.database import Base, engine
from .db import models


app = FastAPI()

# routers
app.include_router(root.router)

# creating tables

Base.metadata.create_all(bind=engine)

