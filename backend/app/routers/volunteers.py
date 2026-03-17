import threading
import traceback
import uuid
from collections import defaultdict, deque
from datetime import datetime
import logging
from typing import Optional
from fastapi import APIRouter, Depends, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from starlette import status
from .. import auth, database, models, schemas
from ..api_utils import api_success


router = APIRouter(prefix="/volunteers", tags=["volunteers"])
logger = logging.getLogger("volunteer")
_RATE_LIMIT_COUNT = 20
_RATE_LIMIT_WINDOW_SECONDS = 60
_rate_lock = threading.Lock()
_rate_bucket = defaultdict(deque)


def _mask_phone(phone: str) -> str:
    if len(phone) < 7:
        return "***"
    return f"{phone[:3]}****{phone[-4:]}"


def _mask_email(email: Optional[str]) -> Optional[str]:
    if not email:
        return email
    if "@" not in email:
        return "***"
    local, domain = email.split("@", 1)
    if len(local) <= 1:
        return f"*@{domain}"
    return f"{local[0]}***@{domain}"


def _extract_request_id(request: Request) -> str:
    state_id = getattr(request.state, "request_id", None)
    if state_id:
        return str(state_id)
    header_id = request.headers.get("X-Request-ID")
    if header_id:
        return header_id
    return str(uuid.uuid4())


def _rate_limit_check(request: Request) -> Optional[JSONResponse]:
    ip = request.client.host if request.client else "unknown"
    now = datetime.utcnow().timestamp()
    with _rate_lock:
        q = _rate_bucket[ip]
        while q and now - q[0] > _RATE_LIMIT_WINDOW_SECONDS:
            q.popleft()
        if len(q) >= _RATE_LIMIT_COUNT:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "code": 4290,
                    "message": "请求过于频繁，请稍后再试",
                    "data": {"limit": _RATE_LIMIT_COUNT, "window_seconds": _RATE_LIMIT_WINDOW_SECONDS},
                },
            )
        q.append(now)
    return None


def _bad_request(fields: list[dict]):
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={"code": 4001, "message": "字段校验失败", "data": {"fields": fields}},
    )


def _internal_error(request_id: str):
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"code": 5000, "message": "服务器内部错误", "data": {"trace_id": request_id}},
    )


def _notify_user_volunteer_status(user_id: int, volunteer_id: int, status_value: str):
    logger.info(
        "volunteer_status_notify user_id=%s volunteer_id=%s status=%s",
        user_id,
        volunteer_id,
        status_value,
    )


@router.get("")
@router.get("/")
def list_volunteers(
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.get_current_admin_user),
):
    rows = (
        db.query(models.Volunteer)
        .order_by(models.Volunteer.created_at.desc(), models.Volunteer.volunteer_id.desc())
        .all()
    )
    items = [
        {
            "volunteer_id": row.volunteer_id,
            "user_id": row.user_id,
            "name": row.name,
            "phone": row.phone,
            "email": row.email,
            "status": row.status,
            "note": row.note,
            "created_at": row.created_at.isoformat() if row.created_at else None,
            "updated_at": row.updated_at.isoformat() if row.updated_at else None,
        }
        for row in rows
    ]
    return api_success({"items": items})


@router.post("/register")
def register_volunteer(
    payload: dict,
    request: Request,
    db: Session = Depends(database.get_db),
):
    request_id = _extract_request_id(request)
    limited = _rate_limit_check(request)
    if limited:
        return limited

    raw_payload = dict(payload or {})
    if not raw_payload.get("note") and raw_payload.get("reason"):
        raw_payload["note"] = raw_payload.get("reason")

    try:
        data = schemas.VolunteerRegisterRequest.model_validate(raw_payload)
    except Exception as exc:
        fields = []
        if hasattr(exc, "errors"):
            for e in exc.errors():
                fields.append(
                    {
                        "field": ".".join([str(part) for part in e.get("loc", [])]),
                        "reason": e.get("msg", "字段非法"),
                    }
                )
        if not fields:
            fields = [{"field": "payload", "reason": "请求体非法"}]
        logger.warning("volunteer_register_invalid request_id=%s fields=%s", request_id, fields)
        return _bad_request(fields)

    logger.info(
        "volunteer_register_request request_id=%s user_id=%s phone=%s email=%s",
        request_id,
        data.user_id,
        _mask_phone(data.phone),
        _mask_email(data.email),
    )

    try:
        with db.begin():
            user = db.query(models.User).filter(models.User.id == data.user_id).first()
            if not user:
                return _bad_request([{"field": "user_id", "reason": "用户不存在"}])

            existing = db.query(models.Volunteer).filter(models.Volunteer.user_id == data.user_id).first()
            if existing:
                return api_success(
                    {"volunteer_id": existing.volunteer_id, "existed": True},
                    message="用户已注册，返回已存在记录",
                )

            volunteer = models.Volunteer(
                user_id=data.user_id,
                name=data.name,
                phone=data.phone,
                email=data.email,
                note=data.note,
                status="未审核",
            )
            db.add(volunteer)
            db.flush()
            volunteer_id = volunteer.volunteer_id

        return api_success({"volunteer_id": volunteer_id, "existed": False}, message="注册成功")
    except IntegrityError as exc:
        db.rollback()
        existing = db.query(models.Volunteer).filter(models.Volunteer.user_id == data.user_id).first()
        if existing:
            return api_success(
                {"volunteer_id": existing.volunteer_id, "existed": True},
                message="用户已注册，返回已存在记录",
            )
        logger.error(
            "volunteer_register_conflict request_id=%s error=%s stack=%s",
            request_id,
            str(exc),
            traceback.format_exc(),
        )
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content={"code": 4090, "message": "user_id 已注册志愿者", "data": {"user_id": data.user_id}},
        )
    except Exception as exc:
        db.rollback()
        logger.error(
            "volunteer_register_error request_id=%s error=%s stack=%s",
            request_id,
            str(exc),
            traceback.format_exc(),
        )
        return _internal_error(request_id)


@router.patch("/{volunteer_id}/status")
def update_volunteer_status(
    volunteer_id: int,
    payload: schemas.VolunteerStatusUpdateRequest,
    request: Request,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.get_current_admin_user),
):
    request_id = _extract_request_id(request)
    try:
        volunteer = db.query(models.Volunteer).filter(models.Volunteer.volunteer_id == volunteer_id).first()
        if not volunteer:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"code": 4040, "message": "志愿者记录不存在", "data": {"volunteer_id": volunteer_id}},
            )
        volunteer.status = payload.status
        user_id = volunteer.user_id
        db.commit()

        _notify_user_volunteer_status(user_id=user_id, volunteer_id=volunteer_id, status_value=payload.status)
        return api_success(
            {"volunteer_id": volunteer_id, "status": payload.status},
            message="志愿者审核状态更新成功",
        )
    except Exception as exc:
        db.rollback()
        logger.error(
            "volunteer_status_update_error request_id=%s volunteer_id=%s error=%s stack=%s",
            request_id,
            volunteer_id,
            str(exc),
            traceback.format_exc(),
        )
        return _internal_error(request_id)


@router.patch("/{volunteer_id}/note")
def update_volunteer_note(
    volunteer_id: int,
    payload: schemas.VolunteerNoteUpdateRequest,
    request: Request,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.get_current_admin_user),
):
    request_id = _extract_request_id(request)
    try:
        volunteer = db.query(models.Volunteer).filter(models.Volunteer.volunteer_id == volunteer_id).first()
        if not volunteer:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"code": 4040, "message": "志愿者记录不存在", "data": {"volunteer_id": volunteer_id}},
            )
        volunteer.note = payload.note
        db.commit()
        return api_success(
            {"volunteer_id": volunteer_id, "note": volunteer.note},
            message="备注更新成功",
        )
    except Exception as exc:
        db.rollback()
        logger.error(
            "volunteer_note_update_error request_id=%s volunteer_id=%s error=%s stack=%s",
            request_id,
            volunteer_id,
            str(exc),
            traceback.format_exc(),
        )
        return _internal_error(request_id)


@router.get("/my")
def get_my_volunteer(
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    volunteer = db.query(models.Volunteer).filter(models.Volunteer.user_id == current_user.user_id).first()
    if not volunteer:
        return api_success({"item": None}, message="当前用户未报名志愿者")
    return api_success(
        {
            "item": {
                "volunteer_id": volunteer.volunteer_id,
                "user_id": volunteer.user_id,
                "name": volunteer.name,
                "phone": volunteer.phone,
                "email": volunteer.email,
                "status": volunteer.status,
                "note": volunteer.note,
                "created_at": volunteer.created_at.isoformat() if volunteer.created_at else None,
                "updated_at": volunteer.updated_at.isoformat() if volunteer.updated_at else None,
            }
        }
    )


@router.delete("/my")
def delete_my_volunteer(
    request: Request,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    request_id = _extract_request_id(request)
    try:
        volunteer = db.query(models.Volunteer).filter(models.Volunteer.user_id == current_user.user_id).first()
        if not volunteer:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"code": 4040, "message": "志愿者记录不存在", "data": {"user_id": current_user.user_id}},
            )
        if volunteer.status != "未审核":
            return JSONResponse(
                status_code=status.HTTP_400_BAD_REQUEST,
                content={"code": 4002, "message": "仅未审核状态可取消报名", "data": {"status": volunteer.status}},
            )
        volunteer_id = volunteer.volunteer_id
        db.delete(volunteer)
        db.commit()
        return api_success({"volunteer_id": volunteer_id}, message="取消报名成功")
    except Exception as exc:
        db.rollback()
        logger.error(
            "volunteer_delete_my_error request_id=%s user_id=%s error=%s stack=%s",
            request_id,
            current_user.user_id,
            str(exc),
            traceback.format_exc(),
        )
        return _internal_error(request_id)


@router.delete("/{volunteer_id}")
def delete_volunteer(
    volunteer_id: int,
    request: Request,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.get_current_admin_user),
):
    request_id = _extract_request_id(request)
    try:
        volunteer = db.query(models.Volunteer).filter(models.Volunteer.volunteer_id == volunteer_id).first()
        if not volunteer:
            return JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"code": 4040, "message": "志愿者记录不存在", "data": {"volunteer_id": volunteer_id}},
            )
        db.delete(volunteer)
        db.commit()
        return api_success({"volunteer_id": volunteer_id}, message="删除成功")
    except Exception as exc:
        db.rollback()
        logger.error(
            "volunteer_delete_error request_id=%s volunteer_id=%s error=%s stack=%s",
            request_id,
            volunteer_id,
            str(exc),
            traceback.format_exc(),
        )
        return _internal_error(request_id)
