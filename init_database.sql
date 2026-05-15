-- =============================================
-- 校园跑腿系统 - 数据库初始化脚本
-- 目标数据库：SQL Server (LocalDB / Express)
-- =============================================

-- 创建数据库
IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = 'CampusErrand')
BEGIN
    CREATE DATABASE CampusErrand;
END
GO

USE CampusErrand;
GO

-- ==================== 用户表 ====================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Users' AND xtype='U')
BEGIN
    CREATE TABLE Users (
        username    VARCHAR(50) PRIMARY KEY,
        password    VARCHAR(100) NOT NULL,
        role        VARCHAR(20) NOT NULL CHECK (role IN ('requester', 'delivery', 'admin')),
        name        NVARCHAR(50) NOT NULL,
        phone       VARCHAR(20) NOT NULL,
        student_id  VARCHAR(50) DEFAULT '',
        rating      FLOAT DEFAULT 0.0,
        completed   INT DEFAULT 0,
        balance     DECIMAL(10,2) DEFAULT 0.0,
        created_at  DATETIME DEFAULT GETDATE()
    );
END
GO

-- ==================== 订单表 ====================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Orders' AND xtype='U')
BEGIN
    CREATE TABLE Orders (
        id              VARCHAR(50) PRIMARY KEY,
        requester       VARCHAR(50) NOT NULL,
        type            NVARCHAR(50) NOT NULL,
        details         NVARCHAR(500) NOT NULL,
        pickup          NVARCHAR(200) NOT NULL,
        dropoff         NVARCHAR(200) NOT NULL,
        reward          DECIMAL(10,2) NOT NULL,
        note            NVARCHAR(200) DEFAULT '',
        status          NVARCHAR(20) DEFAULT '待接单' CHECK (status IN ('待接单', '配送中', '已完成', '已取消')),
        delivery_person VARCHAR(50) DEFAULT NULL,
        created_at      VARCHAR(20),
        accepted_at     VARCHAR(20) DEFAULT NULL,
        completed_at    VARCHAR(20) DEFAULT NULL
    );
END
GO

-- ==================== 评价表 ====================
IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='Reviews' AND xtype='U')
BEGIN
    CREATE TABLE Reviews (
        order_id        VARCHAR(50) PRIMARY KEY,
        requester       VARCHAR(50) NOT NULL,
        delivery_person VARCHAR(50) NOT NULL,
        rating          INT NOT NULL CHECK (rating >= 1 AND rating <= 5),
        comment         NVARCHAR(500) DEFAULT ''
    );
END
GO

-- ==================== 测试数据 ====================
-- 管理员账号
IF NOT EXISTS (SELECT 1 FROM Users WHERE username = 'admin')
BEGIN
    INSERT INTO Users (username, password, role, name, phone, student_id, rating, completed)
    VALUES ('admin', '123456', 'admin', '管理员', '13800138000', 'ADMIN001', 0, 0);
END
GO

-- 需求方账号
IF NOT EXISTS (SELECT 1 FROM Users WHERE username = 'zhangsan')
BEGIN
    INSERT INTO Users (username, password, role, name, phone, student_id, rating, completed)
    VALUES ('zhangsan', '123456', 'requester', '张三', '13900139000', '2024001', 0, 0);
END
GO

-- 配送员账号
IF NOT EXISTS (SELECT 1 FROM Users WHERE username = 'lisi')
BEGIN
    INSERT INTO Users (username, password, role, name, phone, student_id, rating, completed)
    VALUES ('lisi', '123456', 'delivery', '李四', '13700137000', '2024002', 5.0, 0);
END
GO

-- 测试订单
IF NOT EXISTS (SELECT 1 FROM Orders WHERE id = 'TEST001')
BEGIN
    INSERT INTO Orders (id, requester, type, details, pickup, dropoff, reward, note, status, delivery_person, created_at)
    VALUES ('TEST001', 'zhangsan', '快递代取', '帮我取一下快递，在菜鸟驿站3号货架', '菜鸟驿站', '学苑公寓3号楼', 5.0, '到了打电话', '配送中', 'lisi', FORMAT(GETDATE(), 'yyyy-MM-dd HH:mm:ss'));
END
GO

IF NOT EXISTS (SELECT 1 FROM Orders WHERE id = 'TEST002')
BEGIN
    INSERT INTO Orders (id, requester, type, details, pickup, dropoff, reward, note, status, created_at)
    VALUES ('TEST002', 'zhangsan', '外卖代送', '午餐外卖，送到图书馆', '学校东门', '图书馆二楼自习区', 3.0, '不要辣', '待接单', FORMAT(GETDATE(), 'yyyy-MM-dd HH:mm:ss'));
END
GO

PRINT '✅ 数据库初始化完成！';
GO
