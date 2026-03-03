from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from datetime import timedelta
from .. import database, models, auth, schemas
from ..wechat import wechat_client
import logging

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/auth/wechat",
    tags=["authentication"],
    responses={404: {"description": "Not found"}},
)

@router.post("/login", response_model=schemas.Token)
async def wechat_login(request: schemas.WeChatLoginRequest, db: Session = Depends(database.get_db)):
    """
    WeChat One-Click Login
    1. Verify code with WeChat to get openid
    2. Optional: Verify phone_code with WeChat to get phone number (if provided)
    3. Auto-register or login user
    """
    logger.info(f"WeChat login attempt with code length: {len(request.code)}")
    
    # 1. Get OpenID (Moved up as it's always required)
    try:
        session_info = await wechat_client.code_2_session(request.code)
        openid = session_info["openid"]
    except Exception as e:
         logger.error(f"Failed to get session info: {e}")
         raise HTTPException(status_code=400, detail=f"WeChat session verification failed: {str(e)}")

    # 2. Get Phone Number (Optional)
    phone_number = None
    if request.phone_code:
        try:
            phone_info = await wechat_client.get_phone_number(request.phone_code)
            phone_number = phone_info["phoneNumber"]
        except Exception as e:
            logger.error(f"Failed to get phone number: {e}")
            # If phone verification fails but we have openid, we might still proceed or fail?
            # For strict mode, fail. For lenient, maybe proceed without phone.
            # But the request included phone_code, so user intended to provide it.
            # Let's fail if phone_code was provided but invalid.
            raise HTTPException(status_code=400, detail=f"WeChat phone verification failed: {str(e)}")

    # 3. Find or Create User
    # Strategy:
    # - If we have phone_number, find by phone first.
    # - If no phone_number or not found by phone, find by openid.
    
    user = None
    if phone_number:
        user = db.query(models.User).filter(models.User.phone_number == phone_number).first()
    
    if not user:
        user = db.query(models.User).filter(models.User.openid == openid).first()
    
    if not user:
        # Create new user
        logger.info(f"Creating new user for openid: {openid}")
        
        if phone_number:
            username = f"wx_{phone_number}"
        else:
            # Generate username from openid (truncate to keep it reasonable)
            username = f"wx_{openid[-8:]}_{int(timedelta(minutes=0).total_seconds())}" # Append timestamp-like if needed for uniqueness, but openid is unique enough per app usually.
            # Better: use full openid or a slice. OpenID is 28 chars usually.
            username = f"wx_{openid}"
        
        # Ensure username is unique
        existing_username = db.query(models.User).filter(models.User.username == username).first()
        if existing_username:
             import time
             username = f"{username}_{int(time.time())}"

        new_user = models.User(
            username=username,
            phone_number=phone_number,
            openid=openid,
            role="user",
            is_active=True
        )
        db.add(new_user)
        try:
            db.commit()
            db.refresh(new_user)
            user = new_user
        except IntegrityError:
            db.rollback()
            # Race condition: user was created by another request concurrently
            logger.warning(f"IntegrityError creating user {username}, assuming concurrent creation")
            # Try finding again
            user = db.query(models.User).filter(models.User.openid == openid).first()
            if not user and phone_number:
                 user = db.query(models.User).filter(models.User.phone_number == phone_number).first()
            
            if not user:
                 raise HTTPException(status_code=500, detail="Database integrity error")
        except Exception as e:
            db.rollback()
            logger.error(f"Database error creating user: {e}")
            raise HTTPException(status_code=500, detail="Database error")
    else:
        # Update info if needed
        updated = False
        if user.openid != openid:
            user.openid = openid
            updated = True
        if phone_number and user.phone_number != phone_number:
            user.phone_number = phone_number
            updated = True
            
        if updated:
            db.commit()

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    # 4. Create Token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}
