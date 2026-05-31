from fastapi import APIRouter

from .. import schemas
from ..api_utils import ApiError, api_success


router = APIRouter(prefix="/api/products", tags=["products"])


def product_image_url(filename: str) -> str:
    return f"/uploads/product_img/{filename}"


PRODUCTS = {
    "tshirt": {
        "id": "tshirt",
        "title": "T恤",
        "name": "T恤",
        "desc": "300g纯棉双纱紧密赛络纺，OVERSIZE宽松版型。",
        "summary": "纯棉宽松版型，适合日常穿着与文创展示。",
        "meta": "M-L-XL-XXL",
        "colors": [
            {"name": "黑色", "label": "黑色", "value": "#1d1d1f", "image_url": product_image_url("tshirt_black.jpg")},
            {"name": "深灰", "label": "深灰", "value": "#4f5357", "image_url": product_image_url("tshirt_charcoal.jpg")},
            {"name": "浅灰", "label": "浅灰", "value": "#c8c9c7", "image_url": product_image_url("tshirt_lightgray.jpg")},
        ],
        "specs": [
            {"label": "材质", "value": "300g纯棉双纱紧密赛络纺"},
            {"label": "颜色", "value": "深灰、浅灰、黑色"},
            {"label": "版型", "value": "OVERSIZE宽松版型"},
            {"label": "尺码", "value": "M、L、XL、XXL"},
        ],
    },
    "vest": {
        "id": "vest",
        "title": "马甲",
        "name": "马甲",
        "desc": "多功能马甲，后背可脱卸，速干透气。",
        "summary": "多功能穿搭单品，后背可脱卸，适合户外和日常场景。",
        "meta": "S-M-L-XL",
        "colors": [
            {"name": "黑色", "label": "黑色", "value": "#111214", "image_url": product_image_url("vest_black.jpg")},
            {"name": "灰色", "label": "灰色", "value": "#8c8f91", "image_url": product_image_url("vest_gray.jpg")},
        ],
        "specs": [
            {"label": "材质", "value": "100%锦纶面料 + 100%聚酯纤维网布"},
            {"label": "特点", "value": "多功能马甲，后背可脱卸，速干透气"},
            {"label": "颜色", "value": "黑色、灰色"},
            {"label": "尺码", "value": "S、M、L、XL"},
        ],
    },
    "cap": {
        "id": "cap",
        "title": "帽子",
        "name": "帽子",
        "desc": "速干材质，吸湿快干、透气防晒。",
        "summary": "速干材质帽款，适合晴天出行与户外活动。",
        "meta": "头围56-58cm",
        "colors": [
            {
                "name": "米紫",
                "label": "米紫",
                "value": "linear-gradient(135deg,#d7c9af 50%,#6d5aa7 50%)",
                "image_url": product_image_url("cap_beige_purple.jpg"),
            },
            {
                "name": "米黄",
                "label": "米黄",
                "value": "linear-gradient(135deg,#d7c9af 50%,#e6c94b 50%)",
                "image_url": product_image_url("cap_beige_yellow.jpg"),
            },
            {
                "name": "黑绿",
                "label": "黑绿",
                "value": "linear-gradient(135deg,#1b1d1e 50%,#4b8a54 50%)",
                "image_url": product_image_url("cap_black_green.jpg"),
            },
            {
                "name": "灰白",
                "label": "灰白",
                "value": "linear-gradient(135deg,#9c9fa3 50%,#f0f1ef 50%)",
                "image_url": product_image_url("cap_gray_white.jpg"),
            },
        ],
        "specs": [
            {"label": "材质", "value": "速干材质"},
            {"label": "特点", "value": "吸湿快干、透气防晒"},
            {"label": "颜色", "value": "米紫、米黄、黑绿、灰白"},
            {"label": "尺码", "value": "头围56-58cm，帽深12cm"},
        ],
    },
    "cup": {
        "id": "cup",
        "title": "水杯",
        "name": "水杯",
        "desc": "双层不锈钢防烫隔冷，255ML容量。",
        "summary": "双层不锈钢杯身，防烫隔冷，适合随身携带。",
        "meta": "255ML",
        "colors": [
            {"name": "黑色", "label": "黑色", "value": "#171819", "image_url": product_image_url("cup_black.jpg")},
            {"name": "蓝色", "label": "蓝色", "value": "#2e6bb7", "image_url": product_image_url("cup_blue.jpg")},
            {"name": "绿色", "label": "绿色", "value": "#49875a", "image_url": product_image_url("cup_green.jpg")},
            {"name": "橙色", "label": "橙色", "value": "#de7c2d", "image_url": product_image_url("cup_orange.jpg")},
            {"name": "紫色", "label": "紫色", "value": "#7753a6", "image_url": product_image_url("cup_purple.jpg")},
            {"name": "红色", "label": "红色", "value": "#ba3931", "image_url": product_image_url("cup_red.jpg")},
            {"name": "黄色", "label": "黄色", "value": "#e6c542", "image_url": product_image_url("cup_yellow.jpg")},
        ],
        "specs": [
            {"label": "材质", "value": "不锈钢原色内壁，双层不锈钢防烫隔冷"},
            {"label": "颜色", "value": "红色、蓝色、黄色、黑色、紫色、绿色、橙色"},
            {"label": "容量", "value": "255ML"},
            {"label": "尺寸", "value": "杯高8.5cm，杯宽7.5cm"},
        ],
    },
}


def serialize_product(product: dict) -> dict:
    colors = product["colors"]
    return {
        **product,
        "color_count": len(colors),
        "primary_image_url": colors[0]["image_url"] if colors else "",
    }


@router.get("", response_model=schemas.ApiResponse)
@router.get("/", response_model=schemas.ApiResponse)
def list_products():
    return api_success(
        {"items": [serialize_product(item) for item in PRODUCTS.values()]},
        message="加载成功",
    )


@router.get("/{product_id}", response_model=schemas.ApiResponse)
def get_product(product_id: str):
    product = PRODUCTS.get(product_id)
    if not product:
        raise ApiError(code=4004, message="产品不存在", http_status=404)
    return api_success({"item": serialize_product(product)}, message="加载成功")
