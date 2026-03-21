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


class VolunteerRegisterRequest(BaseModel):
    user_id: int = Field(gt=0)
    name: constr(strip_whitespace=True, min_length=1, max_length=30)
    gender: constr(strip_whitespace=True, min_length=1, max_length=10)
    id_card: constr(strip_whitespace=True, min_length=15, max_length=18)
    age: int = Field(ge=1, le=120)
    ethnicity: constr(strip_whitespace=True, min_length=1, max_length=30)
    phone: constr(strip_whitespace=True, min_length=11, max_length=11)
    service_time: constr(strip_whitespace=True, min_length=1, max_length=100)
    organization: constr(strip_whitespace=True, min_length=1, max_length=120)
    position: constr(strip_whitespace=True, min_length=1, max_length=120)
    email: Optional[constr(strip_whitespace=True, max_length=100)] = None
    note: Optional[constr(strip_whitespace=True, max_length=2000)] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, value: str):
        if not value.isdigit():
            raise ValueError("手机号必须为数字")
        return value

    @field_validator("id_card")
    @classmethod
    def validate_id_card(cls, value: str):
        import re
        normalized = value.upper()
        if not re.match(r"^\d{15}$|^\d{17}[\dX]$", normalized):
            raise ValueError("身份证格式不正确")
        return normalized

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: Optional[str]):
        if value is None or value == "":
            return None
        import re
        if not re.match(r"^[^\s@]+@[^\s@]+\.[^\s@]+$", value):
            raise ValueError("邮箱格式不正确")
        return value


class VolunteerRegisterResponse(BaseModel):
    volunteer_id: int
    existed: bool


class VolunteerStatusUpdateRequest(BaseModel):
    status: str

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str):
        if value not in {"已审核", "未审核"}:
            raise ValueError("status 仅支持 已审核/未审核")
        return value


class VolunteerNoteUpdateRequest(BaseModel):
    note: Optional[constr(strip_whitespace=True, max_length=2000)] = None


class VolunteerOut(BaseModel):
    volunteer_id: int
    user_id: int
    name: str
    gender: Optional[str] = None
    id_card: Optional[str] = None
    age: Optional[int] = None
    ethnicity: Optional[str] = None
    phone: str
    service_time: Optional[str] = None
    organization: Optional[str] = None
    position: Optional[str] = None
    email: Optional[str] = None
    status: str
    note: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AudioExplanationCreateRequest(BaseModel):
    title: constr(strip_whitespace=True, min_length=1, max_length=255)
    audio_url: constr(strip_whitespace=True, min_length=1, max_length=1024)
    description: Optional[constr(strip_whitespace=True, max_length=2000)] = None
    status: constr(strip_whitespace=True, min_length=1, max_length=20) = "draft"
    qr_code_url: Optional[constr(strip_whitespace=True, max_length=1024)] = None

    @field_validator("status")
    @classmethod
    def validate_status(cls, value: str):
        if value not in {"draft", "published"}:
            raise ValueError("status 仅支持 draft/published")
        return value


class AudioExplanationOut(BaseModel):
    id: int
    title: str
    audio_url: str
    description: Optional[str] = None
    status: str
    qr_code_url: Optional[str] = None
    created_by: int
    created_at: datetime

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
