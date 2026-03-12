from datetime import datetime, timedelta
from typing import Optional
import logging
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from . import models, schemas, database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Secret key for JWT encoding/decoding
SECRET_KEY = "your-secret-key-should-be-in-env-file"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")
oauth2_scheme_optional = OAuth2PasswordBearer(tokenUrl="api/token", auto_error=False)

def process_password(password: str) -> str:
    """
    Ensure password is not longer than 72 bytes (bcrypt limit).
    Truncate if necessary and log a warning.
    """
    # Encode to bytes to check actual byte length
    password_bytes = password.encode('utf-8')
    if len(password_bytes) > 72:
        logger.warning("Password exceeds 72 bytes. Truncating for bcrypt compatibility.")
        # Truncate to 72 bytes
        return password_bytes[:72].decode('utf-8', errors='ignore')
    return password

def verify_password(plain_password, hashed_password):
    processed_password = process_password(plain_password)
    return pwd_context.verify(processed_password, hashed_password)

def get_password_hash(password):
    processed_password = process_password(password)
    return pwd_context.hash(processed_password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = db.query(models.User).filter(models.User.username == username).first()
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

async def get_current_admin_user(current_user: models.User = Depends(get_current_active_user)):
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="The user doesn't have enough privileges"
        )
    return current_user

async def get_current_user_optional(token: Optional[str] = Depends(oauth2_scheme_optional), db: Session = Depends(database.get_db)):
    if not token:
        return None
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return None
    except JWTError:
        return None
    
    user = db.query(models.User).filter(models.User.username == username).first()
    return user
