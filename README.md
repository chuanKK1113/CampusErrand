# 校园跑腿系统

基于原有 Python tkinter 桌面应用重构的微信小程序 + Web 管理后台。

## 项目结构

```
校园跑腿系统/
├── backend/              # FastAPI 后端 API
│   ├── main.py           # 应用入口，路由注册
│   ├── config.py         # 配置（数据库、JWT等）
│   ├── database.py       # 数据库操作层
│   ├── models.py         # Pydantic 数据模型
│   ├── auth.py           # JWT 认证工具
│   ├── routers/          # API 路由
│   │   ├── users.py      # 用户注册/登录/信息
│   │   ├── orders.py     # 订单 CRUD
│   │   └── reviews.py    # 评价
│   └── requirements.txt  # Python 依赖
│
├── miniprogram/          # 微信小程序
│   ├── app.json/js/wxss  # 应用配置
│   ├── utils/            # 工具（API封装）
│   ├── pages/            # 页面
│   │   ├── login/        # 登录
│   │   ├── register/     # 注册
│   │   ├── home/         # 首页（角色自适应）
│   │   ├── create-order/ # 发布订单
│   │   ├── order-list/   # 订单列表（含筛选）
│   │   ├── order-detail/ # 订单详情（含操作）
│   │   ├── review/       # 评分评价
│   │   ├── income/       # 收入统计（配送员）
│   │   └── profile/      # 个人中心
│   └── images/           # Tab Bar 图标
│
├── web-admin/            # Vue3 管理后台
│   ├── src/
│   │   ├── views/
│   │   │   ├── login/        # 登录页
│   │   │   ├── dashboard/    # 仪表盘（统计）
│   │   │   ├── orders/       # 订单管理
│   │   │   └── users/        # 用户管理
│   │   ├── layouts/          # 后台布局
│   │   ├── api/              # Axios 封装
│   │   ├── stores/           # Pinia 状态
│   │   └── router/           # 路由
│   └── package.json
│
├── init_database.sql     # SQL Server 建表脚本
└── main.py               # 原 tkinter 桌面版
```

## 环境配置

### 1. 数据库（SQL Server）

**方式一：使用 SQL Server LocalDB（推荐开发用）**
1. 安装 [SQL Server LocalDB](https://learn.microsoft.com/zh-cn/sql/database-engine/configure-windows/sql-server-express-localdb)
2. 安装 [ODBC Driver 18 for SQL Server](https://learn.microsoft.com/zh-cn/sql/connect/odbc/download-odbc-driver-for-sql-server)
3. 运行初始化脚本：
```bash
sqlcmd -S "(localdb)\MSSQLLocalDB" -i init_database.sql
```

**方式二：使用 SQL Server Express**
1. 安装 SQL Server Express（启用 `SQLEXPRESS` 实例）
2. 安装 ODBC Driver 18
3. 运行：
```bash
sqlcmd -S "localhost\SQLEXPRESS" -i init_database.sql
```

> 如果使用不同的服务器地址，请修改 `backend/config.py` 中的 `DATABASE_CONFIG`。

### 2. 后端（FastAPI）

```bash
# 安装 Python 依赖
cd backend
pip install -r requirements.txt

# 启动服务（热重载）
python main.py
# 或
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API 文档地址：http://localhost:8000/docs

### 3. 微信小程序

1. 下载安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 打开项目，选择 `miniprogram/` 目录
3. 在工具右上角点击「详情」-「本地设置」- 勾选「不校验合法域名」
4. 确保后端已启动，在小程序 `app.js` 中确认 `baseUrl` 指向后端地址
5. 点击编译预览

### 4. Web 管理后台

```bash
cd web-admin
npm install

# 开发模式启动（需同时启动后端）
npm run dev
```

构建生产版本：
```bash
npm run build
# 输出到 dist/ 目录
```

## 默认测试账号

| 角色 | 用户名 | 密码 | 说明 |
|------|--------|------|------|
| 管理员 | admin | 123456 | 可登录 Web 后台 |
| 需求方 | zhangsan | 123456 | 可发布订单 |
| 配送员 | lisi | 123456 | 可接单配送 |

## 核心功能

### 小程序端（双角色）
| 功能 | 需求方 | 配送员 |
|------|--------|--------|
| 注册/登录 | ✅ | ✅ |
| 发布订单 | ✅ | - |
| 浏览可接单 | - | ✅ |
| 接单配送 | - | ✅ |
| 确认送达 | - | ✅ |
| 我的订单/配送 | ✅ | ✅ |
| 评价配送员 | ✅ | - |
| 收入统计 | - | ✅ |
| 个人中心 | ✅ | ✅ |
| 退出登录 | ✅ | ✅ |

### Web 管理后台
| 功能 | 说明 |
|------|------|
| 管理员登录 | 仅 admin 角色可登录 |
| 数据仪表盘 | 用户数、订单数、进行中/已完成统计 |
| 订单管理 | 查看/搜索/筛选/取消订单 |
| 用户管理 | 查看用户列表、角色统计 |
