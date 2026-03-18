import hashlib
import json
import os
import uuid
from datetime import datetime
from typing import Optional
import bleach
from fastapi import APIRouter, Depends, Header, UploadFile, File
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import Session
from starlette import status
from .. import database, models, schemas, auth
from ..api_utils import ApiError, api_success


router = APIRouter(prefix="/api/consultations", tags=["consultations"])
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads", "consultations")
MAX_IMAGE_SIZE = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/gif"}

ALLOWED_TAGS = [
    "p", "br", "strong", "em", "u", "s", "blockquote", "code", "pre",
    "h1", "h2", "h3", "h4", "h5", "h6", "ul", "ol", "li", "a", "img",
    "table", "thead", "tbody", "tr", "th", "td", "span", "div"
]
ALLOWED_ATTRIBUTES = {
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt", "title", "width", "height"],
    "span": ["style"],
    "div": ["style"],
    "p": ["style"],
    "code": ["class"],
}
ALLOWED_PROTOCOLS = ["http", "https", "mailto"]


def sanitize_html(content: str) -> str:
    cleaned = bleach.clean(
        content,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
    )
    plain = bleach.clean(cleaned, tags=[], strip=True).strip()
    if not plain:
        raise ApiError(code=2001, message="正文内容不能为空", http_status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    return cleaned


def payload_hash(payload: dict) -> str:
    payload_text = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(payload_text.encode("utf-8")).hexdigest()


def check_idempotency(
    db: Session,
    endpoint: str,
    author_id: int,
    idempotency_key: Optional[str],
    request_payload: dict,
):
    if not idempotency_key:
        return None
    req_hash = payload_hash(request_payload)
    record = (
        db.query(models.ConsultationIdempotency)
        .filter(
            models.ConsultationIdempotency.idempotency_key == idempotency_key,
            models.ConsultationIdempotency.author_id == author_id,
            models.ConsultationIdempotency.endpoint == endpoint,
        )
        .first()
    )
    if not record:
        return None
    if record.request_hash != req_hash:
        raise ApiError(code=2002, message="幂等键已存在且请求体不一致", http_status=status.HTTP_409_CONFLICT)
    return json.loads(record.response_body)


def save_idempotency(
    db: Session,
    endpoint: str,
    author_id: int,
    idempotency_key: Optional[str],
    request_payload: dict,
    response_payload: dict,
):
    if not idempotency_key:
        return
    record = models.ConsultationIdempotency(
        idempotency_key=idempotency_key,
        endpoint=endpoint,
        author_id=author_id,
        request_hash=payload_hash(request_payload),
        response_body=json.dumps(response_payload, ensure_ascii=False),
    )
    db.add(record)
    db.commit()


def assert_edit_permission(current_user: models.User, news: models.Consultation):
    if current_user.role == "admin":
        return
    if news.author_id != current_user.id:
        raise ApiError(code=2003, message="无权限操作该咨询", http_status=status.HTTP_403_FORBIDDEN)


@router.post("/upload-image", response_model=schemas.ApiResponse)
async def upload_consultation_image(
    file: UploadFile = File(...),
    _: models.User = Depends(auth.get_current_active_user),
):
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise ApiError(code=2010, message="仅支持 JPG/PNG/WEBP/GIF 图片", http_status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    content = await file.read()
    if not content:
        raise ApiError(code=2011, message="上传文件为空", http_status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if len(content) > MAX_IMAGE_SIZE:
        raise ApiError(code=2012, message="图片大小不能超过5MB", http_status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in {".jpg", ".jpeg", ".png", ".webp", ".gif"}:
        ext = ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(content)
    image_url = f"/uploads/consultations/{filename}"
    return api_success({"url": image_url}, message="上传成功")


@router.post("", response_model=schemas.ApiResponse)
def create_consultation(
    payload: schemas.ConsultationCreate,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    request_payload = payload.model_dump()
    idem = check_idempotency(db, "create_consultation", current_user.id, idempotency_key, request_payload)
    if idem:
        return api_success(idem, message="重复提交已拦截，返回历史结果")

    cleaned_content = sanitize_html(payload.content)
    news = models.Consultation(
        title=payload.title,
        cover=payload.cover,
        content=cleaned_content,
        author_id=current_user.id,
        status=payload.status,
    )
    db.add(news)
    db.flush()

    version = models.ConsultationVersion(
        consultation_id=news.id,
        version_no=1,
        title=news.title,
        content=news.content,
        editor_id=current_user.id,
    )
    db.add(version)
    db.commit()
    db.refresh(news)

    data = {"id": str(news.id), "status": news.status}
    save_idempotency(db, "create_consultation", current_user.id, idempotency_key, request_payload, data)
    return api_success(data, message="创建成功")


@router.put("/{consultation_id}", response_model=schemas.ApiResponse)
def update_consultation(
    consultation_id: int,
    payload: schemas.ConsultationUpdate,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    news = db.query(models.Consultation).filter(models.Consultation.id == consultation_id).first()
    if not news:
        raise ApiError(code=2004, message="咨询不存在", http_status=status.HTTP_404_NOT_FOUND)
    assert_edit_permission(current_user, news)

    request_payload = payload.model_dump(exclude_none=True)
    if not request_payload:
        raise ApiError(code=2005, message="没有可更新字段", http_status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    idem = check_idempotency(
        db, f"update_consultation:{consultation_id}", current_user.id, idempotency_key, request_payload
    )
    if idem:
        return api_success(idem, message="重复提交已拦截，返回历史结果")

    if payload.title is not None:
        news.title = payload.title
    if payload.cover is not None:
        news.cover = payload.cover
    if payload.content is not None:
        news.content = sanitize_html(payload.content)
    if payload.status is not None:
        news.status = payload.status

    max_version = (
        db.query(func.max(models.ConsultationVersion.version_no))
        .filter(models.ConsultationVersion.consultation_id == consultation_id)
        .scalar()
    )
    version = models.ConsultationVersion(
        consultation_id=news.id,
        version_no=(max_version or 0) + 1,
        title=news.title,
        content=news.content,
        editor_id=current_user.id,
    )
    db.add(version)
    db.commit()
    db.refresh(news)

    data = {"id": str(news.id), "status": news.status, "updated_at": news.updated_at.isoformat()}
    save_idempotency(
        db, f"update_consultation:{consultation_id}", current_user.id, idempotency_key, request_payload, data
    )
    return api_success(data, message="更新成功")


@router.patch("/{consultation_id}/status", response_model=schemas.ApiResponse)
def update_consultation_status(
    consultation_id: int,
    payload: schemas.ConsultationStatusUpdate,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    news = db.query(models.Consultation).filter(models.Consultation.id == consultation_id).first()
    if not news:
        raise ApiError(code=2004, message="咨询不存在", http_status=status.HTTP_404_NOT_FOUND)
    assert_edit_permission(current_user, news)

    request_payload = payload.model_dump()
    idem = check_idempotency(
        db, f"update_consultation_status:{consultation_id}", current_user.id, idempotency_key, request_payload
    )
    if idem:
        return api_success(idem, message="重复提交已拦截，返回历史结果")

    news.status = payload.status
    db.commit()
    db.refresh(news)

    data = {"id": str(news.id), "status": news.status}
    save_idempotency(
        db,
        f"update_consultation_status:{consultation_id}",
        current_user.id,
        idempotency_key,
        request_payload,
        data,
    )
    return api_success(data, message="状态更新成功")


@router.post("/bulk/status", response_model=schemas.ApiResponse)
def bulk_update_status(
    payload: schemas.ConsultationBulkStatusUpdate,
    idempotency_key: Optional[str] = Header(default=None, alias="Idempotency-Key"),
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_active_user),
):
    request_payload = payload.model_dump()
    idem = check_idempotency(db, "bulk_update_status", current_user.id, idempotency_key, request_payload)
    if idem:
        return api_success(idem, message="重复提交已拦截，返回历史结果")

    query = db.query(models.Consultation).filter(models.Consultation.id.in_(payload.ids))
    if current_user.role != "admin":
        query = query.filter(models.Consultation.author_id == current_user.id)
    news_list = query.all()
    if not news_list:
        raise ApiError(code=2006, message="未找到可操作的咨询记录", http_status=status.HTTP_404_NOT_FOUND)

    for news in news_list:
        news.status = payload.status
    db.commit()

    data = {"updated_count": len(news_list), "status": payload.status}
    save_idempotency(db, "bulk_update_status", current_user.id, idempotency_key, request_payload, data)
    return api_success(data, message="批量状态更新成功")


@router.get("", response_model=schemas.ApiResponse)
def list_consultations(
    status_value: Optional[int] = None,
    author_id: Optional[int] = None,
    keyword: Optional[str] = None,
    start_time: Optional[datetime] = None,
    end_time: Optional[datetime] = None,
    page: int = 1,
    page_size: int = 10,
    db: Session = Depends(database.get_db),
    current_user: Optional[models.User] = Depends(auth.get_current_user_optional),
):
    if page < 1 or page_size < 1 or page_size > 100:
        raise ApiError(code=1001, message="分页参数非法", http_status=status.HTTP_422_UNPROCESSABLE_ENTITY)

    query = db.query(models.Consultation)
    filters = []
    if status_value in (0, 1):
        filters.append(models.Consultation.status == status_value)
    elif current_user is None or current_user.role != "admin":
        filters.append(models.Consultation.status == 1)
    if author_id is not None:
        filters.append(models.Consultation.author_id == author_id)
    if keyword:
        like_value = f"%{keyword}%"
        filters.append(or_(models.Consultation.title.ilike(like_value), models.Consultation.content.ilike(like_value)))
    if start_time:
        filters.append(models.Consultation.created_at >= start_time)
    if end_time:
        filters.append(models.Consultation.created_at <= end_time)
    if filters:
        query = query.filter(and_(*filters))

    total = query.count()
    items = (
        query.order_by(models.Consultation.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    return api_success(
        {
            "total": total,
            "page": page,
            "page_size": page_size,
            "items": [schemas.ConsultationOut.model_validate(item).model_dump() for item in items],
        }
    )


@router.get("/{consultation_id}", response_model=schemas.ApiResponse)
def get_consultation(
    consultation_id: int,
    db: Session = Depends(database.get_db),
    current_user: Optional[models.User] = Depends(auth.get_current_user_optional),
):
    item = db.query(models.Consultation).filter(models.Consultation.id == consultation_id).first()
    if not item:
        raise ApiError(code=2004, message="咨询不存在", http_status=status.HTTP_404_NOT_FOUND)
    if current_user is None and item.status != 1:
        raise ApiError(code=2004, message="咨询不存在", http_status=status.HTTP_404_NOT_FOUND)
    return api_success(schemas.ConsultationOut.model_validate(item).model_dump())


@router.delete("/{consultation_id}", response_model=schemas.ApiResponse)
def delete_consultation(
    consultation_id: int,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.get_current_admin_user),
):
    news = db.query(models.Consultation).filter(models.Consultation.id == consultation_id).first()
    if not news:
        raise ApiError(code=2004, message="咨询不存在", http_status=status.HTTP_404_NOT_FOUND)
    db.query(models.ConsultationVersion).filter(
        models.ConsultationVersion.consultation_id == consultation_id
    ).delete(synchronize_session=False)
    db.delete(news)
    db.commit()
    return api_success({"id": str(consultation_id)}, message="删除成功")


@router.get("/{consultation_id}/versions", response_model=schemas.ApiResponse)
def get_consultation_versions(
    consultation_id: int,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.get_current_active_user),
):
    news = db.query(models.Consultation).filter(models.Consultation.id == consultation_id).first()
    if not news:
        raise ApiError(code=2004, message="咨询不存在", http_status=status.HTTP_404_NOT_FOUND)
    versions = (
        db.query(models.ConsultationVersion)
        .filter(models.ConsultationVersion.consultation_id == consultation_id)
        .order_by(models.ConsultationVersion.version_no.desc())
        .all()
    )
    return api_success(
        {"items": [schemas.ConsultationVersionOut.model_validate(v).model_dump() for v in versions]}
    )
