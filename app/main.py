"""
FastAPI 애플리케이션 진입점
메인 애플리케이션 초기화 및 라우터 등록
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

from app.config import settings
from app.database import engine, Base

# FastAPI 앱 생성
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    debug=settings.DEBUG
)

# HTTPS 리버스 프록시 헤더 처리 (Nginx SSL 종단 시 url_for가 https:// 생성하도록)
app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")

# CORS 미들웨어 설정 (필요한 경우)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 정적 파일 마운트
app.mount("/static", StaticFiles(directory="static"), name="static")

# Jinja2 템플릿 설정
templates = Jinja2Templates(directory="app/templates")


# 라우터 등록 (나중에 추가)
from app.routers import cattle_router, breeding_record_router, cattle_note_router, event_log_router
app.include_router(cattle_router.router, prefix="/api/cattle", tags=["Cattle"])
app.include_router(breeding_record_router.router, prefix="/api/breeding", tags=["Breeding"])
app.include_router(cattle_note_router.router, prefix="/api/notes", tags=["Notes"])
app.include_router(event_log_router.router, prefix="/api/events", tags=["Events"])
# app.include_router(statistics_router.router, prefix="/api/statistics", tags=["Statistics"])
# app.include_router(export_router.router, prefix="/api/export", tags=["Export"])

# 페이지 라우터 등록
from app.pages import dashboard, cattle_page

app.include_router(dashboard.router, tags=["Pages"])
app.include_router(cattle_page.router, tags=["Pages"])


@app.on_event("startup")
async def startup_event():
    """애플리케이션 시작 시 실행"""
    print("🚀 Livestock Management System 시작 중...")
    print(f"📊 데이터베이스: {settings.DATABASE_URL.split('@')[1]}")  # 비밀번호 제외하고 출력
    
    # 데이터베이스 테이블 생성 (개발 중에만, 나중에는 Alembic 사용)
    # Base.metadata.create_all(bind=engine)


@app.on_event("shutdown")
async def shutdown_event():
    """애플리케이션 종료 시 실행"""
    print("🛑 Livestock Management System 종료 중...")


@app.get("/")
async def root():
    """
    루트 엔드포인트 - API 상태 확인
    나중에 대시보드 페이지로 리다이렉트 또는 템플릿 렌더링
    """
    return {
        "message": "🐄 Livestock Management System API",
        "version": settings.VERSION,
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "database": "connected"}


if __name__ == "__main__":
    import uvicorn
    
    # 서버 실행
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,        # DEBUG 모드일 때만 자동 리로드
        reload_dirs=["app", "static"] # Windows WinError 10014 방지: 감시 대상 폴더 명시
    )