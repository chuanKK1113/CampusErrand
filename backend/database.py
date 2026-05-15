"""数据库连接与操作层 - 支持 SQLite（开发）和 SQL Server（生产）"""

import sqlite3
import uuid
from datetime import datetime
from contextlib import contextmanager

from config import DB_TYPE, SQLITE_PATH, CONNECTION_STR


# ==================== 连接管理 ====================

@contextmanager
def get_db():
    """获取数据库连接的上下文管理器（自动提交/回滚）"""
    if DB_TYPE == "sqlite":
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
    else:
        import pyodbc
        conn = pyodbc.connect(CONNECTION_STR)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def row_to_dict(cursor, row):
    """将数据库行转换为字典"""
    if DB_TYPE == "sqlite":
        return dict(row) if row else None
    else:
        if not row:
            return None
        columns = [col[0] for col in cursor.description]
        return dict(zip(columns, row))


def rows_to_list(cursor, rows):
    """将多行转换为字典列表"""
    return [row_to_dict(cursor, r) for r in rows] if rows else []


# ==================== SQL 方言适配 ====================

def ifnull_expr(column, default):
    """跨数据库的 IFNULL/ISNULL 表达式"""
    if DB_TYPE == "sqlite":
        return f"IFNULL({column}, {default})"
    return f"ISNULL({column}, {default})"


# ==================== 初始化 ====================

def init_database():
    """初始化数据库表结构（仅 SQLite 需要建表，SQL Server 用 init_database.sql）"""
    if DB_TYPE != "sqlite":
        return
    with get_db() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS Users (
                username    TEXT PRIMARY KEY,
                password    TEXT NOT NULL,
                role        TEXT NOT NULL CHECK (role IN ('requester', 'delivery', 'admin')),
                name        TEXT NOT NULL,
                phone       TEXT NOT NULL,
                student_id  TEXT DEFAULT '',
                rating      REAL DEFAULT 0.0,
                completed   INTEGER DEFAULT 0,
                balance     REAL DEFAULT 0.0,
                created_at  TEXT
            );

            CREATE TABLE IF NOT EXISTS Orders (
                id              TEXT PRIMARY KEY,
                requester       TEXT NOT NULL,
                type            TEXT NOT NULL,
                details         TEXT NOT NULL,
                pickup          TEXT NOT NULL,
                dropoff         TEXT NOT NULL,
                reward          REAL NOT NULL,
                note            TEXT DEFAULT '',
                status          TEXT DEFAULT '待接单' CHECK (status IN ('待接单', '配送中', '已完成', '已取消')),
                delivery_person TEXT DEFAULT NULL,
                created_at      TEXT,
                accepted_at     TEXT DEFAULT NULL,
                completed_at    TEXT DEFAULT NULL
            );

            CREATE TABLE IF NOT EXISTS Reviews (
                order_id        TEXT PRIMARY KEY,
                requester       TEXT NOT NULL,
                delivery_person TEXT NOT NULL,
                rating          INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
                comment         TEXT DEFAULT ''
            );
        """)

        # 插入测试数据
        cursor = conn.cursor()
        if not cursor.execute("SELECT 1 FROM Users WHERE username='admin'").fetchone():
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO Users VALUES (?,?,?,?,?,?,?,?,?,?)",
                           ("admin", "123456", "admin", "管理员", "13800138000", "ADMIN001", 0, 0, 0, now))
            cursor.execute("INSERT INTO Users VALUES (?,?,?,?,?,?,?,?,?,?)",
                           ("zhangsan", "123456", "requester", "张三", "13900139000", "2024001", 0, 0, 0, now))
            cursor.execute("INSERT INTO Users VALUES (?,?,?,?,?,?,?,?,?,?)",
                           ("lisi", "123456", "delivery", "李四", "13700137000", "2024002", 5.0, 0, 0, now))
            cursor.execute(
                "INSERT INTO Orders (id, requester, type, details, pickup, dropoff, reward, note, status, delivery_person, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                ("TEST001", "zhangsan", "快递代取", "帮我取一下快递，在菜鸟驿站3号货架",
                 "菜鸟驿站", "学苑公寓3号楼", 5.0, "到了打电话", "配送中", "lisi", now)
            )
            cursor.execute(
                "INSERT INTO Orders (id, requester, type, details, pickup, dropoff, reward, note, status, created_at) VALUES (?,?,?,?,?,?,?,?,?,?)",
                ("TEST002", "zhangsan", "外卖代送", "午餐外卖，送到图书馆",
                 "学校东门", "图书馆二楼自习区", 3.0, "不要辣", "待接单", now)
            )


# ==================== 数据库操作 ====================

class Database:
    """数据库操作类 - 封装所有 SQL 查询"""

    # ==================== 用户相关 ====================

    @staticmethod
    def register(username, password, role, name, phone, student_id=""):
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT username FROM Users WHERE username = ?", (username,))
            if cur.fetchone():
                return False, "用户名已存在"

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                "INSERT INTO Users (username, password, role, name, phone, student_id, rating, completed, balance, created_at) VALUES (?,?,?,?,?,?,0,0,0,?)",
                (username, password, role, name, phone, student_id, now),
            )
            return True, "注册成功"

    @staticmethod
    def login(username, password):
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Users WHERE username = ? AND password = ?",
                        (username, password))
            row = cur.fetchone()
            if not row:
                return None
            user = row_to_dict(cur, row)
            if user:
                user.pop("password", None)
            return user

    @staticmethod
    def get_user(username):
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                "SELECT username, role, name, phone, student_id, rating, completed, balance, created_at FROM Users WHERE username = ?",
                (username,))
            return row_to_dict(cur, cur.fetchone())

    @staticmethod
    def get_all_users():
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT username, role, name, phone, student_id, rating, completed, balance, created_at FROM Users")
            return rows_to_list(cur, cur.fetchall())

    # ==================== 订单相关 ====================

    @staticmethod
    def create_order(requester, order_type, details, pickup, dropoff, reward, note=""):
        with get_db() as conn:
            cur = conn.cursor()
            order_id = uuid.uuid4().hex[:8]
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute(
                "INSERT INTO Orders (id, requester, type, details, pickup, dropoff, reward, note, status, created_at) VALUES (?,?,?,?,?,?,?,?,'待接单',?)",
                (order_id, requester, order_type, details, pickup, dropoff, reward, note, now),
            )
            return True, "创建成功", order_id

    @staticmethod
    def get_order(order_id):
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Orders WHERE id = ?", (order_id,))
            return row_to_dict(cur, cur.fetchone())

    @staticmethod
    def get_available_orders():
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Orders WHERE status = '待接单' ORDER BY reward DESC")
            return rows_to_list(cur, cur.fetchall())

    @staticmethod
    def get_orders_by_user(username, status=None):
        with get_db() as conn:
            cur = conn.cursor()
            if status:
                cur.execute("SELECT * FROM Orders WHERE requester = ? AND status = ? ORDER BY created_at DESC",
                            (username, status))
            else:
                cur.execute("SELECT * FROM Orders WHERE requester = ? ORDER BY created_at DESC", (username,))
            return rows_to_list(cur, cur.fetchall())

    @staticmethod
    def get_orders_by_delivery(username, status=None):
        with get_db() as conn:
            cur = conn.cursor()
            if status:
                cur.execute("SELECT * FROM Orders WHERE delivery_person = ? AND status = ? ORDER BY accepted_at DESC",
                            (username, status))
            else:
                cur.execute("SELECT * FROM Orders WHERE delivery_person = ? ORDER BY accepted_at DESC", (username,))
            return rows_to_list(cur, cur.fetchall())

    @staticmethod
    def get_all_orders():
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Orders ORDER BY created_at DESC")
            return rows_to_list(cur, cur.fetchall())

    @staticmethod
    def accept_order(order_id, delivery_person):
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT status FROM Orders WHERE id = ?", (order_id,))
            row = cur.fetchone()
            if not row:
                return False, "订单不存在"
            status = row["status"] if DB_TYPE == "sqlite" else row[0]
            if status != "待接单":
                return False, f"订单当前状态为「{status}」，无法接单"

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("UPDATE Orders SET status = '配送中', delivery_person = ?, accepted_at = ? WHERE id = ?",
                        (delivery_person, now, order_id))
            return True, "接单成功"

    @staticmethod
    def complete_order(order_id):
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT status FROM Orders WHERE id = ?", (order_id,))
            row = cur.fetchone()
            if not row:
                return False, "订单不存在"
            status = row["status"] if DB_TYPE == "sqlite" else row[0]
            if status != "配送中":
                return False, f"订单当前状态为「{status}」，无法确认送达"

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cur.execute("UPDATE Orders SET status = '已完成', completed_at = ? WHERE id = ?", (now, order_id))
            cur.execute(
                "UPDATE Users SET completed = completed + 1 WHERE username = (SELECT delivery_person FROM Orders WHERE id = ?)",
                (order_id,))
            return True, "已确认送达"

    @staticmethod
    def cancel_order(order_id):
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT status FROM Orders WHERE id = ?", (order_id,))
            row = cur.fetchone()
            if not row:
                return False, "订单不存在"
            status = row["status"] if DB_TYPE == "sqlite" else row[0]
            if status != "待接单":
                return False, f"订单当前状态为「{status}」，无法取消"
            cur.execute("UPDATE Orders SET status = '已取消' WHERE id = ?", (order_id,))
            return True, "订单已取消"

    # ==================== 评价相关 ====================

    @staticmethod
    def add_review(order_id, requester, delivery_person, rating, comment=""):
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT order_id FROM Reviews WHERE order_id = ?", (order_id,))
            if cur.fetchone():
                return False, "该订单已被评价"

            cur.execute("INSERT INTO Reviews (order_id, requester, delivery_person, rating, comment) VALUES (?,?,?,?,?)",
                        (order_id, requester, delivery_person, rating, comment))

            # 重新计算配送员的平均评分
            cur.execute("SELECT AVG(rating) FROM Reviews WHERE delivery_person = ?", (delivery_person,))
            avg_rating = cur.fetchone()[0]
            cur.execute("UPDATE Users SET rating = ? WHERE username = ?",
                        (round(avg_rating if avg_rating else 0, 1), delivery_person))
            return True, "评价成功"

    @staticmethod
    def review_exists(order_id):
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT order_id FROM Reviews WHERE order_id = ?", (order_id,))
            return cur.fetchone() is not None

    @staticmethod
    def get_reviews_by_requester(username):
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Reviews WHERE requester = ? ORDER BY order_id DESC", (username,))
            return rows_to_list(cur, cur.fetchall())

    @staticmethod
    def get_reviews_by_delivery(username):
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute("SELECT * FROM Reviews WHERE delivery_person = ? ORDER BY order_id DESC", (username,))
            return rows_to_list(cur, cur.fetchall())

    # ==================== 统计相关 ====================

    @staticmethod
    def get_stats():
        with get_db() as conn:
            cur = conn.cursor()
            stats = {}
            cur.execute("SELECT COUNT(*) FROM Users")
            stats["total_users"] = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM Orders")
            stats["total_orders"] = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM Orders WHERE status = '配送中'")
            stats["active_orders"] = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM Orders WHERE status = '已完成'")
            stats["completed_orders"] = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM Orders WHERE status = '待接单'")
            stats["pending_orders"] = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM Users WHERE role = 'requester'")
            stats["total_requesters"] = cur.fetchone()[0]
            cur.execute("SELECT COUNT(*) FROM Users WHERE role = 'delivery'")
            stats["total_delivery"] = cur.fetchone()[0]
            return stats

    @staticmethod
    def get_delivery_income(username):
        with get_db() as conn:
            cur = conn.cursor()
            cur.execute(
                f"SELECT COUNT(*), {ifnull_expr('SUM(reward)', '0')} FROM Orders WHERE delivery_person = ? AND status = '已完成'",
                (username,))
            row = cur.fetchone()
            vals = (row["COUNT(*)"], row[ifnull_expr('SUM(reward)', '0')]) if DB_TYPE == "sqlite" else (row[0], row[1])
            return {"completed_count": vals[0], "total_income": float(vals[1])}
