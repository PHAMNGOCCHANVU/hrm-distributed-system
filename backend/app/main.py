from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.db_router import close_all_pools
from app.api.routes import (
    auth, employees, payroll, catalogs, system,
    organizations, appointments, admin_requests, reports
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Khởi chạy ứng dụng
    yield
    # Dọn dẹp tài nguyên khi tắt ứng dụng
    close_all_pools()


app = FastAPI(
    title="SpaceX HRM Distributed System API",
    description="Hệ thống Quản trị Nhân sự & Lương Phân tán Đa Chi nhánh SpaceX (Enterprise Model)",
    version="2.0.0",
    lifespan=lifespan
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler tùy chỉnh để chuẩn hóa JSON Error Envelope theo Section 3.1
@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    detail = exc.detail
    if isinstance(detail, dict):
        code = detail.get("code", f"HTTP_{exc.status_code}")
        message = detail.get("message", "Đã có lỗi xảy ra")
        details = detail.get("details", None)
    elif isinstance(detail, str):
        code = f"HTTP_{exc.status_code}"
        message = detail
        details = None
    else:
        code = f"HTTP_{exc.status_code}"
        message = str(detail)
        details = None

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": code,
                "message": message,
                "details": details
            }
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Dữ liệu đầu vào không hợp lệ",
                "details": exc.errors()
            }
        }
    )


@app.get("/")
def root():
    return {
        "success": True,
        "message": "SpaceX HRM Distributed Backend is running (Enterprise Edition)",
        "version": "2.0.0"
    }


# Đăng ký các Router phân hệ với tiền tố /api
app.include_router(auth.router, prefix="/api")
app.include_router(employees.router, prefix="/api")
app.include_router(payroll.router, prefix="/api")
app.include_router(catalogs.router, prefix="/api")
app.include_router(system.router, prefix="/api")
app.include_router(organizations.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(admin_requests.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
