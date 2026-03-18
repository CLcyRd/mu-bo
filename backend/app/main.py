from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
import os
import uuid
load_dotenv()

from . import models, database
from .database import engine
from .routers import bookings, auth, auth_wechat, users, consultations, volunteers
from .api_utils import api_success, register_exception_handlers

models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Museum Booking API")
register_exception_handlers(app)

default_origins = [
    "http://localhost",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
    "https://shxiejinf.cn",
    "https://www.shxiejinf.cn",
    "https://api.shxiejinf.cn",
]
env_origins = os.getenv("ALLOW_ORIGINS", "")
origins = [item.strip() for item in env_origins.split(",") if item.strip()] or default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_request_id(request, call_next):
    rid = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    request.state.request_id = rid
    response = await call_next(request)
    response.headers["X-Request-ID"] = rid
    return response

app.include_router(bookings.router)
app.include_router(auth.router)
app.include_router(auth_wechat.router)
app.include_router(users.router)
app.include_router(consultations.router)
app.include_router(volunteers.router)
app.include_router(volunteers.router, prefix="/api")
uploads_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

@app.get("/")
def read_root():
    return api_success({"service": "Museum Booking API"}, "服务运行正常")
