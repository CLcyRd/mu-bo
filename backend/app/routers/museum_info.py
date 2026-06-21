import os

from fastapi import APIRouter

from .. import schemas
from ..api_utils import api_success


router = APIRouter(prefix="/api/museum-info", tags=["museum_info"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
BANNER_DIR = os.path.join(BASE_DIR, "uploads", "museum_img")
BANNER_URL_PREFIX = "/uploads/museum_img"
PROMO_VIDEO_DIR = os.path.join(BASE_DIR, "uploads", "promo_video")
PROMO_VIDEO_FILENAME = "4df64ebb9bb9147b5424899f4caaba92_h264.mp4"
PROMO_VIDEO_COVER_FILENAME = "4df64ebb9bb9147b5424899f4caaba92_cover.jpg"
PROMO_VIDEO_URL_PREFIX = "/uploads/promo_video"
ALLOWED_IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def _list_banner_files() -> list[str]:
    if not os.path.isdir(BANNER_DIR):
        return []
    names = []
    for entry in os.listdir(BANNER_DIR):
        full_path = os.path.join(BANNER_DIR, entry)
        if not os.path.isfile(full_path):
            continue
        ext = os.path.splitext(entry)[1].lower()
        if ext not in ALLOWED_IMAGE_EXTS:
            continue
        if entry.startswith("default_"):
            continue
        names.append(entry)
    names.sort()
    return names


@router.get("/banners", response_model=schemas.ApiResponse)
def list_banners():
    items = [
        {"filename": name, "url": f"{BANNER_URL_PREFIX}/{name}"}
        for name in _list_banner_files()
    ]
    return api_success({"items": items}, message="加载成功")


@router.get("/homepage-media", response_model=schemas.ApiResponse)
def list_homepage_media():
    items = []
    video_path = os.path.join(PROMO_VIDEO_DIR, PROMO_VIDEO_FILENAME)
    cover_path = os.path.join(PROMO_VIDEO_DIR, PROMO_VIDEO_COVER_FILENAME)
    if os.path.isfile(video_path) and os.path.isfile(cover_path):
        items.append(
            {
                "type": "video",
                "title": "走进谢晋故居",
                "subtitle": "宣传视频 · 点击全屏播放",
                "cover_url": f"{PROMO_VIDEO_URL_PREFIX}/{PROMO_VIDEO_COVER_FILENAME}",
                "video_url": f"{PROMO_VIDEO_URL_PREFIX}/{PROMO_VIDEO_FILENAME}",
            }
        )

    items.extend(
        {"type": "image", "filename": name, "url": f"{BANNER_URL_PREFIX}/{name}"}
        for name in _list_banner_files()
    )
    return api_success({"items": items}, message="加载成功")
