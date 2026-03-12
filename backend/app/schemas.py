from pydantic import BaseModel, Field, constr, field_validator
from typing import Optional, List
from datetime import date, datetime


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


class ApiResponse(BaseModel):
    code: int = 0
    message: str = "success"
    data: Optional[dict] = None


class ConsultationBase(BaseModel):
    title: constr(strip_whitespace=True, min_length=1, max_length=100)
    cover: constr(strip_whitespace=True, max_length=1024) = ""
    content: str = Field(..., strip_whitespace=True, min_length=1, max_length=200000)


class ConsultationCreate(ConsultationBase):
    status: int = Field(default=0, ge=0, le=1)


class ConsultationUpdate(BaseModel):
    title: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None
    cover: Optional[constr(strip_whitespace=True, max_length=1024)] = None
    content: Optional[constr(strip_whitespace=True, min_length=1, max_length=200000)] = None
    status: Optional[int] = Field(default=None, ge=0, le=1)


class ConsultationStatusUpdate(BaseModel):
    status: int = Field(ge=0, le=1)


class ConsultationBulkStatusUpdate(BaseModel):
    ids: List[int] = Field(default_factory=list, min_length=1)
    status: int = Field(ge=0, le=1)


class ConsultationQuery(BaseModel):
    status: Optional[int] = Field(default=None, ge=0, le=1)
    author_id: Optional[int] = None
    keyword: Optional[str] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class ConsultationOut(BaseModel):
    id: str
    title: str
    cover: str
    content: str
    author_id: int
    created_at: datetime
    updated_at: datetime
    status: int

    @field_validator("id", mode="before")
    @classmethod
    def cast_id_to_str(cls, v):
        return str(v)

    class Config:
        from_attributes = True


class ConsultationVersionOut(BaseModel):
    id: str
    consultation_id: str
    version_no: int
    title: str
    content: str
    editor_id: int
    created_at: datetime

    @field_validator("id", "consultation_id", mode="before")
    @classmethod
    def cast_version_ids_to_str(cls, v):
        return str(v)

    class Config:
        from_attributes = True
