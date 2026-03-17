import logging
import os
import traceback
import uuid
from logging.handlers import RotatingFileHandler
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette import status


def setup_error_file_logger():
    logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(logs_dir, exist_ok=True)
    logger = logging.getLogger("app.error")
    if logger.handlers:
        return logger
    logger.setLevel(logging.INFO)
    handler = RotatingFileHandler(
        os.path.join(logs_dir, "app.log"),
        maxBytes=5 * 1024 * 1024,
        backupCount=5,
        encoding="utf-8",
    )
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


class ApiError(Exception):
    def __init__(self, code: int, message: str, http_status: int = status.HTTP_400_BAD_REQUEST):
        self.code = code
        self.message = message
        self.http_status = http_status
        super().__init__(message)


def api_success(data=None, message: str = "success", code: int = 0):
    return {"code": code, "message": message, "data": data}


def register_exception_handlers(app):
    error_logger = setup_error_file_logger()

    def request_id(request: Request) -> str:
        state_id = getattr(request.state, "request_id", None)
        if state_id:
            return str(state_id)
        return request.headers.get("X-Request-ID", str(uuid.uuid4()))

    @app.exception_handler(ApiError)
    async def handle_api_error(request: Request, exc: ApiError):
        rid = request_id(request)
        error_logger.error(
            "request_id=%s path=%s method=%s api_error=%s stack=%s",
            rid,
            request.url.path,
            request.method,
            exc.message,
            traceback.format_exc(),
        )
        return JSONResponse(
            status_code=exc.http_status,
            content={"code": exc.code, "message": exc.message, "data": None},
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError):
        rid = request_id(request)
        error_logger.error(
            "request_id=%s path=%s method=%s validation_error=%s stack=%s",
            rid,
            request.url.path,
            request.method,
            str(exc),
            traceback.format_exc(),
        )
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"code": 1001, "message": "请求参数校验失败", "data": exc.errors()},
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException):
        rid = request_id(request)
        error_logger.error(
            "request_id=%s path=%s method=%s http_error=%s stack=%s",
            rid,
            request.url.path,
            request.method,
            str(exc.detail),
            traceback.format_exc(),
        )
        return JSONResponse(
            status_code=exc.status_code,
            content={"code": 1000, "message": str(exc.detail), "data": None},
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, exc: Exception):
        rid = request_id(request)
        error_logger.error(
            "request_id=%s path=%s method=%s unexpected_error=%s stack=%s",
            rid,
            request.url.path,
            request.method,
            str(exc),
            traceback.format_exc(),
        )
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"code": 5000, "message": "服务器内部错误", "data": {"trace_id": rid}},
        )
