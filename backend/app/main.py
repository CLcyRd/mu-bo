from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

from . import models, schemas, database
from .database import engine
from .routers import exhibits, bookings, auth, auth_wechat, users

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Museum Booking API")

origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

app.include_router(exhibits.router)
app.include_router(bookings.router)
app.include_router(auth.router)
app.include_router(auth_wechat.router)
app.include_router(users.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to Museum Booking API"}
