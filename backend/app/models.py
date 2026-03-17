import time
import threading
from sqlalchemy import Column, Integer, BigInteger, String, Boolean, Date, DateTime, ForeignKey, Text, Index, UniqueConstraint, Enum, func
from sqlalchemy.orm import relationship
from .database import Base

_SNOWFLAKE_LOCK = threading.Lock()
_SNOWFLAKE_LAST_MS = 0
_SNOWFLAKE_SEQ = 0
_SNOWFLAKE_NODE_ID = 1


def generate_snowflake_id() -> int:
    global _SNOWFLAKE_LAST_MS, _SNOWFLAKE_SEQ
    with _SNOWFLAKE_LOCK:
        now_ms = int(time.time() * 1000)
        if now_ms == _SNOWFLAKE_LAST_MS:
            _SNOWFLAKE_SEQ = (_SNOWFLAKE_SEQ + 1) & 0xFFF
            if _SNOWFLAKE_SEQ == 0:
                while now_ms <= _SNOWFLAKE_LAST_MS:
                    now_ms = int(time.time() * 1000)
        else:
            _SNOWFLAKE_SEQ = 0
        _SNOWFLAKE_LAST_MS = now_ms
        epoch = 1704067200000
        return ((now_ms - epoch) << 22) | (_SNOWFLAKE_NODE_ID << 12) | _SNOWFLAKE_SEQ

    
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


class Consultation(Base):
    __tablename__ = "consultation"
    __table_args__ = (
        Index("ix_consultation_title_fulltext", "title", mysql_prefix="FULLTEXT"),
    )

    id = Column(BigInteger, primary_key=True, default=generate_snowflake_id)
    title = Column(String(255), nullable=False, index=True)
    cover = Column(String(1024), nullable=False, default="")
    content = Column(Text, nullable=False)
    author_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    status = Column(Integer, default=0, nullable=False, index=True)

    author = relationship("User", backref="consultations")


class ConsultationVersion(Base):
    __tablename__ = "consultation_versions"

    id = Column(BigInteger, primary_key=True, default=generate_snowflake_id)
    consultation_id = Column(BigInteger, ForeignKey("consultation.id"), nullable=False, index=True)
    version_no = Column(Integer, nullable=False)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    editor_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

    consultation = relationship("Consultation", backref="versions")
    editor = relationship("User")


class ConsultationIdempotency(Base):
    __tablename__ = "consultation_idempotency"
    __table_args__ = (
        UniqueConstraint("idempotency_key", "author_id", name="uq_consultation_idempotency"),
    )

    id = Column(BigInteger, primary_key=True, default=generate_snowflake_id)
    idempotency_key = Column(String(128), nullable=False, index=True)
    endpoint = Column(String(128), nullable=False)
    author_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True)
    request_hash = Column(String(64), nullable=False)
    response_body = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)


class Volunteer(Base):
    __tablename__ = "volunteers"

    volunteer_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    name = Column(String(30), nullable=False)
    phone = Column(String(11), nullable=False)
    email = Column(String(100), nullable=True)
    status = Column(Enum("已审核", "未审核", name="volunteer_status", native_enum=False), nullable=False, default="未审核")
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)

    user = relationship("User", backref="volunteer_profile")
