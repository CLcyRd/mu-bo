from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from .. import crud, models, schemas, database, auth

router = APIRouter(
    prefix="/api/bookings",
    tags=["bookings"],
    responses={404: {"description": "Not found"}},
)

@router.post("/", response_model=dict)
def create_booking(
    booking: schemas.BookingCreate, 
    db: Session = Depends(database.get_db),
    current_user: Optional[models.User] = Depends(auth.get_current_user_optional)
):
    user_id = current_user.user_id if current_user else None
    db_booking = crud.create_booking(db=db, booking=booking, user_id=user_id)
    return {"booking_id": db_booking.booking_id, "status": db_booking.status}

@router.get("/my", response_model=List[schemas.Booking])
def read_my_bookings(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Get current user's bookings
    """
    bookings = db.query(models.Booking).filter(models.Booking.user_id == current_user.user_id).order_by(models.Booking.visit_date.desc(), models.Booking.visit_time.desc()).all()
    return bookings

@router.delete("/{booking_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_booking(
    booking_id: str,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user)
):
    """
    Delete a booking
    """
    booking = db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
        
    # Check ownership
    if not (booking.user_id == current_user.user_id or current_user.role == "admin"):
        raise HTTPException(status_code=403, detail="Not authorized to delete this booking")
        
    db.delete(booking)
    db.commit()
    return None

@router.get("/", response_model=List[schemas.Booking])
def read_bookings(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_admin_user)
):
    bookings = crud.get_bookings(db, skip=skip, limit=limit)
    return bookings
