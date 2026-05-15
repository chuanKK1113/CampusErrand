"""校园跑腿系统 - FastAPI 后端入口"""

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from config import APP_TITLE, APP_DESCRIPTION, APP_VERSION, UPLOAD_DIR
from database import init_database
from routers.users import router as auth_router
from routers.users import admin_router as users_admin_router
from routers.orders import router as orders_router
from routers.orders import admin_router as orders_admin_router
from routers.reviews import router as reviews_router

# 启动时自动初始化数据库（SQLite 建表 + 测试数据）
init_database()

# 确保上传目录存在
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(
    title=APP_TITLE,
    description=APP_DESCRIPTION,
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    redirect_slashes=False,
)

# CORS 配置 - 允许小程序和 Web 管理端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应限制具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录（头像上传）
app.mount("/uploads", StaticFiles(directory=os.path.join(os.path.dirname(__file__), "uploads")), name="uploads")

# 注册路由
app.include_router(auth_router)
app.include_router(users_admin_router)
app.include_router(orders_router)
app.include_router(orders_admin_router)
app.include_router(reviews_router)


@app.get("/")
def root():
    """API 根路径"""
    return {
        "title": APP_TITLE,
        "version": APP_VERSION,
        "docs": "/docs",
    }


@app.get("/api/stats")
def get_stats():
    """获取系统统计数据"""
    from database import Database
    return Database.get_stats()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
