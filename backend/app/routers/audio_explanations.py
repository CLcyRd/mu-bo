import os
import uuid
from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session
from starlette import status
from .. import auth, database, models, schemas
from ..api_utils import ApiError, api_success
from ..wechat import wechat_client

router = APIRouter(prefix="/api/audio-explanations", tags=["audio_explanations"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads", "audio_explanations")
QRCODE_DIR = os.path.join(BASE_DIR, "uploads", "audio_qrcodes")
MINIPROGRAM_AUDIO_PAGE = os.getenv("WECHAT_AUDIO_MINIPROGRAM_PAGE", "pages/audio-guide/player")
ALLOWED_AUDIO_TYPES = {
    "audio/mpeg",
    "audio/mp3",
    "audio/mp4",
    "audio/x-m4a",
    "audio/aac",
    "audio/wav",
    "audio/x-wav",
}
MAX_AUDIO_SIZE = 20 * 1024 * 1024


@router.post("/upload-audio", response_model=schemas.ApiResponse)
async def upload_audio_explanation_file(
    file: UploadFile = File(...),
    _: models.User = Depends(auth.get_current_admin_user),
):
    if file.content_type not in ALLOWED_AUDIO_TYPES:
        raise ApiError(code=3010, message="仅支持 MP3/M4A/AAC/WAV 音频", http_status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)
    content = await file.read()
    if not content:
        raise ApiError(code=3011, message="上传文件为空", http_status=status.HTTP_422_UNPROCESSABLE_ENTITY)
    if len(content) > MAX_AUDIO_SIZE:
        raise ApiError(code=3012, message="音频大小不能超过20MB", http_status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in {".mp3", ".m4a", ".aac", ".wav"}:
        ext = ".mp3"
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(content)
    audio_url = f"/uploads/audio_explanations/{filename}"
    return api_success({"url": audio_url}, message="上传成功")


@router.post("", response_model=schemas.ApiResponse)
@router.post("/", response_model=schemas.ApiResponse)
def create_audio_explanation(
    payload: schemas.AudioExplanationCreateRequest,
    db: Session = Depends(database.get_db),
    current_user: models.User = Depends(auth.get_current_admin_user),
):
    entity = models.AudioExplanation(
        title=payload.title,
        audio_url=payload.audio_url,
        description=payload.description,
        status=payload.status,
        qr_code_url=payload.qr_code_url,
        created_by=current_user.id,
    )
    db.add(entity)
    db.commit()
    db.refresh(entity)
    return api_success(
        {
            "item": {
                "id": entity.id,
                "title": entity.title,
                "audio_url": entity.audio_url,
                "description": entity.description,
                "status": entity.status,
                "qr_code_url": entity.qr_code_url,
                "created_by": entity.created_by,
                "created_at": entity.created_at.isoformat() if entity.created_at else None,
            }
        },
        message="讲解创建成功",
    )


@router.get("", response_model=schemas.ApiResponse)
@router.get("/", response_model=schemas.ApiResponse)
def list_audio_explanations(
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.get_current_admin_user),
):
    rows = (
        db.query(models.AudioExplanation)
        .order_by(models.AudioExplanation.created_at.desc(), models.AudioExplanation.id.desc())
        .all()
    )
    items = [
        {
            "id": row.id,
            "title": row.title,
            "audio_url": row.audio_url,
            "description": row.description,
            "status": row.status,
            "qr_code_url": row.qr_code_url,
            "created_by": row.created_by,
            "created_at": row.created_at.isoformat() if row.created_at else None,
        }
        for row in rows
    ]
    return api_success({"items": items}, message="加载成功")


@router.delete("/{audio_id}", response_model=schemas.ApiResponse)
def delete_audio_explanation(
    audio_id: int,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.get_current_admin_user),
):
    row = db.query(models.AudioExplanation).filter(models.AudioExplanation.id == audio_id).first()
    if not row:
        raise ApiError(code=3040, message="讲解记录不存在", http_status=status.HTTP_404_NOT_FOUND)
    audio_url = row.audio_url or ""
    qr_url = row.qr_code_url or ""
    db.delete(row)
    db.commit()
    if audio_url.startswith("/uploads/audio_explanations/"):
        filename = audio_url.replace("/uploads/audio_explanations/", "")
        file_path = os.path.join(UPLOAD_DIR, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
    if qr_url.startswith("/uploads/audio_qrcodes/"):
        filename = qr_url.replace("/uploads/audio_qrcodes/", "")
        file_path = os.path.join(QRCODE_DIR, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
    return api_success({"id": audio_id}, message="删除成功")


@router.post("/{audio_id}/mini-code", response_model=schemas.ApiResponse)
async def generate_audio_explanation_mini_code(
    audio_id: int,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.get_current_admin_user),
):
    row = db.query(models.AudioExplanation).filter(models.AudioExplanation.id == audio_id).first()
    if not row:
        raise ApiError(code=3040, message="讲解记录不存在", http_status=status.HTTP_404_NOT_FOUND)
    os.makedirs(QRCODE_DIR, exist_ok=True)
    scene = f"id={audio_id}"
    image_bytes = await wechat_client.get_wxacode_unlimit(scene=scene, page=MINIPROGRAM_AUDIO_PAGE)
    filename = f"audio_{audio_id}_{uuid.uuid4().hex}.png"
    file_path = os.path.join(QRCODE_DIR, filename)
    with open(file_path, "wb") as f:
        f.write(image_bytes)
    old_qr_url = row.qr_code_url or ""
    row.qr_code_url = f"/uploads/audio_qrcodes/{filename}"
    db.commit()
    if old_qr_url.startswith("/uploads/audio_qrcodes/"):
        old_name = old_qr_url.replace("/uploads/audio_qrcodes/", "")
        old_path = os.path.join(QRCODE_DIR, old_name)
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except OSError:
                pass
    return api_success({"id": audio_id, "qr_code_url": row.qr_code_url}, message="小程序码生成成功")


@router.get("/{audio_id}/mini-code", response_model=schemas.ApiResponse)
def get_audio_explanation_mini_code(
    audio_id: int,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.get_current_admin_user),
):
    row = db.query(models.AudioExplanation).filter(models.AudioExplanation.id == audio_id).first()
    if not row:
        raise ApiError(code=3040, message="讲解记录不存在", http_status=status.HTTP_404_NOT_FOUND)
    return api_success({"id": audio_id, "qr_code_url": row.qr_code_url}, message="查询成功")


@router.delete("/{audio_id}/mini-code", response_model=schemas.ApiResponse)
def delete_audio_explanation_mini_code(
    audio_id: int,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.get_current_admin_user),
):
    row = db.query(models.AudioExplanation).filter(models.AudioExplanation.id == audio_id).first()
    if not row:
        raise ApiError(code=3040, message="讲解记录不存在", http_status=status.HTTP_404_NOT_FOUND)
    qr_url = row.qr_code_url or ""
    row.qr_code_url = None
    db.commit()
    if qr_url.startswith("/uploads/audio_qrcodes/"):
        filename = qr_url.replace("/uploads/audio_qrcodes/", "")
        file_path = os.path.join(QRCODE_DIR, filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError:
                pass
    return api_success({"id": audio_id}, message="小程序码删除成功")


@router.patch("/{audio_id}/status", response_model=schemas.ApiResponse)
def toggle_audio_explanation_status(
    audio_id: int,
    db: Session = Depends(database.get_db),
    _: models.User = Depends(auth.get_current_admin_user),
):
    row = db.query(models.AudioExplanation).filter(models.AudioExplanation.id == audio_id).first()
    if not row:
        raise ApiError(code=3040, message="讲解记录不存在", http_status=status.HTTP_404_NOT_FOUND)
    row.status = "published" if row.status == "draft" else "draft"
    db.commit()
    return api_success({"id": audio_id, "status": row.status}, message="状态切换成功")
