from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, ForeignKey, func
from sqlalchemy.orm import relationship
from .database import Base

class Exhibit(Base):
    __tablename__ = "exhibits"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String)
    category = Column(String, index=True)
    image_url = Column(String)
    era = Column(String)
    is_featured = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=True)
    hashed_password = Column(String, nullable=True)
    phone_number = Column(String, unique=True, index=True, nullable=True)
    openid = Column(String, unique=True, index=True, nullable=True)
    role = Column(String, default="user") # user, admin
    is_active = Column(Boolean, default=True)

    @property
    def user_id(self):
        return self.id

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    booking_id = Column(String, unique=True, index=True)
    visit_date = Column(Date, index=True)
    visit_time = Column(String)
    visitor_name = Column(String)
    visitor_phone = Column(String)
    visitor_count = Column(Integer)
    status = Column(String, default="pending", index=True) # pending, confirmed, cancelled
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", backref="bookings")
