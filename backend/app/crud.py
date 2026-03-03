from sqlalchemy.orm import Session
from . import models, schemas
import uuid

def get_exhibits(db: Session, skip: int = 0, limit: int = 10, category: str = None):
    query = db.query(models.Exhibit)
    if category:
        query = query.filter(models.Exhibit.category == category)
    return query.offset(skip).limit(limit).all()

def get_exhibits_count(db: Session, category: str = None):
    query = db.query(models.Exhibit)
    if category:
        query = query.filter(models.Exhibit.category == category)
    return query.count()

def create_exhibit(db: Session, exhibit: schemas.ExhibitCreate):
    db_exhibit = models.Exhibit(**exhibit.dict())
    db.add(db_exhibit)
    db.commit()
    db.refresh(db_exhibit)
    return db_exhibit

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
