"""应用配置"""

import os

# 数据库配置
# 可选: 'sqlite' (无需安装, 开发用) 或 'mssql' (SQL Server, 生产用)
DB_TYPE = os.getenv("DB_TYPE", "sqlite")

# SQLite 配置（默认）
SQLITE_PATH = os.path.join(os.path.dirname(__file__), "campus_errand.db")

# SQL Server 配置（需要安装 SQL Server + ODBC Driver 18）
DATABASE_CONFIG = {
    "driver": "{ODBC Driver 18 for SQL Server}",
    "server": "localhost\\SQLEXPRESS",
    "database": "CampusErrand",
    "trusted_connection": "yes",
    "trust_server_certificate": "yes",
}

CONNECTION_STR = ";".join(f"{k}={v}" for k, v in DATABASE_CONFIG.items())

# JWT 配置
SECRET_KEY = "campus-errand-system-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 1440  # 24小时

# 应用配置
APP_TITLE = "校园跑腿系统 API"
APP_DESCRIPTION = "校园跑腿系统后端 RESTful API"
APP_VERSION = "1.0.0"
