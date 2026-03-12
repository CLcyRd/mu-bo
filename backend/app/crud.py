from sqlalchemy.orm import Session
from . import models, schemas
import uuid


def create_booking(db: Session, booking: schemas.BookingCreate, user_id: int = None):
    # Generate a unique booking ID
    booking_id = str(uuid.uuid4())
    db_booking = models.Booking(
        **booking.dict(),
        booking_id=booking_id,
        user_id=user_id
    )
    db.add(db_booking)
    db.commit()
    db.refresh(db_booking)
    return db_booking

def get_bookings(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Booking).offset(skip).limit(limit).all()

def get_booking_by_id(db: Session, booking_id: str):
    return db.query(models.Booking).filter(models.Booking.booking_id == booking_id).first()
