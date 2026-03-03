from pydantic import BaseModel
from typing import Optional, List
from datetime import date, datetime

class ExhibitBase(BaseModel):
    name: str
    description: Optional[str] = None
    category: str
    image_url: Optional[str] = None
    era: Optional[str] = None
    is_featured: bool = False

class ExhibitCreate(ExhibitBase):
    pass

class Exhibit(ExhibitBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    id: int
    user_id: int
    username: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: Optional[bool] = True
    role: str

    class Config:
        from_attributes = True

class WeChatLoginRequest(BaseModel):
    code: str
    phone_code: Optional[str] = None

class BookingBase(BaseModel):
    visit_date: date
    visit_time: str
    visitor_name: str
    visitor_phone: str
    visitor_count: int

class BookingCreate(BookingBase):
    pass

class Booking(BookingBase):
    id: int
    booking_id: str
    status: str
    created_at: datetime
    updated_at: datetime
    user_id: Optional[int] = None

    class Config:
        from_attributes = True
