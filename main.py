"""
校园跑腿系统 - 精简版
基于 tkinter 的桌面应用程序
"""

import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
import uuid
import pyodbc

# ==================== 数据库配置 ====================

DB_CONN_STR = (
    "DRIVER={ODBC Driver 18 for SQL Server};"
    "SERVER=localhost\\SQLEXPRESS;"
    "DATABASE=CampusErrand;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

def get_conn():
    return pyodbc.connect(DB_CONN_STR)

def dict_from_row(row, columns):
    """将数据库行转为字典"""
    return dict(zip(columns, row))


# ==================== 数据层 ====================

class Database:
    """SQL Server 数据库"""
    def __init__(self):
        pass

    # ---- 用户相关 ----

    def register(self, username, password, role, name, phone, student_id=None):
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM [Users] WHERE username = ?", (username,))
            if cursor.fetchone():
                return False, "用户名已存在"
            cursor.execute(
                "INSERT INTO [Users] (username, password, role, name, phone, student_id) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (username, password, role, name, phone, student_id or "")
            )
            conn.commit()
            return True, "注册成功"
        except Exception as e:
            return False, f"注册失败：{str(e)}"
        finally:
            conn.close()

    def login(self, username, password):
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username, password, role, name, phone, student_id, "
                "       rating, completed, balance "
                "FROM [Users] WHERE username = ?", (username,)
            )
            row = cursor.fetchone()
            if not row:
                return False, "用户不存在"
            columns = ["username", "password", "role", "name", "phone",
                       "student_id", "rating", "completed", "balance"]
            user = dict_from_row(row, columns)
            if user["password"] != password:
                return False, "密码错误"
            del user["password"]
            return True, user
        finally:
            conn.close()

    def get_user(self, username):
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username, password, role, name, phone, student_id, "
                "       rating, completed, balance "
                "FROM [Users] WHERE username = ?", (username,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            columns = ["username", "password", "role", "name", "phone",
                       "student_id", "rating", "completed", "balance"]
            user = dict_from_row(row, columns)
            del user["password"]
            return user
        finally:
            conn.close()

    def get_all_users(self):
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT username, password, role, name, phone, student_id, "
                "       rating, completed, balance "
                "FROM [Users] ORDER BY created_at DESC"
            )
            columns = ["username", "password", "role", "name", "phone",
                       "student_id", "rating", "completed", "balance"]
            users = [dict_from_row(r, columns) for r in cursor.fetchall()]
            for u in users:
                del u["password"]
            return users
        finally:
            conn.close()

    # ---- 订单相关 ----

    def create_order(self, requester, order_type, details, pickup_location,
                     dropoff_location, reward, note=""):
        order_id = str(uuid.uuid4())[:8]
        now = datetime.now().strftime("%Y-%m-%d %H:%M")
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO [Orders] (id, requester, type, details, pickup, dropoff, "
                "                     reward, note, status, created_at) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, N'待接单', ?)",
                (order_id, requester, order_type, details, pickup_location,
                 dropoff_location, reward, note, now)
            )
            conn.commit()
            return order_id
        finally:
            conn.close()

    def _row_to_order(self, row, columns):
        o = dict_from_row(row, columns)
        # None 转 None, 保持与之前一致
        return o

    def get_order(self, order_id):
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, requester, type, details, pickup, dropoff, reward, note, "
                "       status, delivery_person, created_at, accepted_at, completed_at "
                "FROM [Orders] WHERE id = ?", (order_id,)
            )
            row = cursor.fetchone()
            if not row:
                return None
            columns = ["id", "requester", "type", "details", "pickup", "dropoff",
                       "reward", "note", "status", "delivery_person",
                       "created_at", "accepted_at", "completed_at"]
            return self._row_to_order(row, columns)
        finally:
            conn.close()

    def get_available_orders(self):
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, requester, type, details, pickup, dropoff, reward, note, "
                "       status, delivery_person, created_at, accepted_at, completed_at "
                "FROM [Orders] WHERE status = N'待接单' ORDER BY reward DESC, created_at DESC"
            )
            columns = ["id", "requester", "type", "details", "pickup", "dropoff",
                       "reward", "note", "status", "delivery_person",
                       "created_at", "accepted_at", "completed_at"]
            return [self._row_to_order(r, columns) for r in cursor.fetchall()]
        finally:
            conn.close()

    def get_orders_by_user(self, username):
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, requester, type, details, pickup, dropoff, reward, note, "
                "       status, delivery_person, created_at, accepted_at, completed_at "
                "FROM [Orders] WHERE requester = ? ORDER BY created_at DESC", (username,)
            )
            columns = ["id", "requester", "type", "details", "pickup", "dropoff",
                       "reward", "note", "status", "delivery_person",
                       "created_at", "accepted_at", "completed_at"]
            return [self._row_to_order(r, columns) for r in cursor.fetchall()]
        finally:
            conn.close()

    def get_orders_by_delivery(self, username):
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, requester, type, details, pickup, dropoff, reward, note, "
                "       status, delivery_person, created_at, accepted_at, completed_at "
                "FROM [Orders] WHERE delivery_person = ? ORDER BY created_at DESC", (username,)
            )
            columns = ["id", "requester", "type", "details", "pickup", "dropoff",
                       "reward", "note", "status", "delivery_person",
                       "created_at", "accepted_at", "completed_at"]
            return [self._row_to_order(r, columns) for r in cursor.fetchall()]
        finally:
            conn.close()

    def get_all_orders(self):
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT id, requester, type, details, pickup, dropoff, reward, note, "
                "       status, delivery_person, created_at, accepted_at, completed_at "
                "FROM [Orders] ORDER BY created_at DESC"
            )
            columns = ["id", "requester", "type", "details", "pickup", "dropoff",
                       "reward", "note", "status", "delivery_person",
                       "created_at", "accepted_at", "completed_at"]
            return [self._row_to_order(r, columns) for r in cursor.fetchall()]
        finally:
            conn.close()

    def accept_order(self, order_id, delivery_person):
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM [Orders] WHERE id = ?", (order_id,))
            row = cursor.fetchone()
            if not row:
                return False, "订单不存在"
            if row[0] != "待接单":
                return False, "订单已被接走"
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            cursor.execute(
                "UPDATE [Orders] SET status = N'配送中', delivery_person = ?, accepted_at = ? "
                "WHERE id = ?",
                (delivery_person, now, order_id)
            )
            conn.commit()
            return True, "接单成功"
        finally:
            conn.close()

    def complete_order(self, order_id):
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT status, delivery_person FROM [Orders] WHERE id = ?", (order_id,))
            row = cursor.fetchone()
            if not row:
                return False, "订单不存在"
            if row[0] != "配送中":
                return False, "订单状态不正确"
            now = datetime.now().strftime("%Y-%m-%d %H:%M")
            dp = row[1]
            cursor.execute(
                "UPDATE [Orders] SET status = N'已完成', completed_at = ? WHERE id = ?",
                (now, order_id)
            )
            if dp:
                cursor.execute(
                    "UPDATE [Users] SET completed = completed + 1 WHERE username = ?", (dp,)
                )
            conn.commit()
            return True, "已确认送达"
        finally:
            conn.close()

    def cancel_order(self, order_id):
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT status FROM [Orders] WHERE id = ?", (order_id,))
            row = cursor.fetchone()
            if not row:
                return False, "订单不存在"
            if row[0] != "待接单":
                return False, "订单已接单，无法取消"
            cursor.execute(
                "UPDATE [Orders] SET status = N'已取消' WHERE id = ?", (order_id,)
            )
            conn.commit()
            return True, "订单已取消"
        finally:
            conn.close()

    # ---- 评价相关 ----

    def add_review(self, order_id, rating, comment):
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT requester, delivery_person FROM [Orders] WHERE id = ?", (order_id,)
            )
            row = cursor.fetchone()
            if not row:
                return False
            requester, dp = row[0], row[1]
            cursor.execute(
                "INSERT INTO [Reviews] (order_id, delivery_person, rating, comment, requester) "
                "VALUES (?, ?, ?, ?, ?)",
                (order_id, dp, rating, comment, requester)
            )
            # 更新配送员平均评分
            if dp:
                cursor.execute(
                    "SELECT AVG(CAST(rating AS FLOAT)) FROM [Reviews] WHERE delivery_person = ?",
                    (dp,)
                )
                avg = cursor.fetchone()[0]
                cursor.execute(
                    "UPDATE [Users] SET rating = ? WHERE username = ?",
                    (round(avg, 1) if avg else 5.0, dp)
                )
            conn.commit()
            return True
        finally:
            conn.close()

    def review_exists(self, order_id):
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM [Reviews] WHERE order_id = ?", (order_id,))
            return cursor.fetchone() is not None
        finally:
            conn.close()

    def get_reviews_by_requester(self, username):
        try:
            conn = get_conn()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT order_id, delivery_person, rating, comment, requester "
                "FROM [Reviews] WHERE requester = ?", (username,)
            )
            columns = ["order_id", "delivery_person", "rating", "comment", "requester"]
            return [dict_from_row(r, columns) for r in cursor.fetchall()]
        finally:
            conn.close()


db = Database()
current_user = None


# ==================== 页面框架 ====================

class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("校园跑腿系统")
        self.geometry("900x650")
        self.minsize(800, 600)

        # 主容器
        self.container = tk.Frame(self)
        self.container.pack(fill="both", expand=True)

        # 页面栈
        self.pages = {}
        self.current_page = None

        # 设置样式
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # 显示登录页
        self.show_page("LoginPage")

    def show_page(self, page_name, **kwargs):
        if self.current_page:
            self.current_page.pack_forget()

        if page_name not in self.pages:
            page_class = globals()[page_name]
            self.pages[page_name] = page_class(self.container, self)

        page = self.pages[page_name]
        if hasattr(page, "on_show") and not kwargs.get("skip_refresh"):
            page.on_show()
        page.pack(fill="both", expand=True)
        self.current_page = page

    def clear_pages(self):
        """清除所有页面（用于登出）"""
        self.pages.clear()
        self.current_page = None


# ==================== 公共组件 ====================

class HeaderFrame(tk.Frame):
    """页面顶部栏"""
    def __init__(self, parent, app, title, show_back=False, back_callback=None):
        super().__init__(parent, bg="#4A90D9", height=50)
        self.pack(fill="x")
        self.pack_propagate(False)

        tk.Label(self, text=title, font=("微软雅黑", 14, "bold"),
                bg="#4A90D9", fg="white").pack(side="left", padx=20, pady=10)

        if show_back:
            btn = tk.Button(self, text="← 返回", font=("微软雅黑", 10),
                          bg="#4A90D9", fg="white", bd=0,
                          activebackground="#357ABD",
                          command=back_callback)
            btn.pack(side="right", padx=10)

        if current_user:
            info = f"{current_user['name']} ({current_user['role']})"
            tk.Label(self, text=info, font=("微软雅黑", 10),
                    bg="#4A90D9", fg="white").pack(side="right", padx=20)

        # 分隔线
        tk.Frame(self, bg="#357ABD", height=2).pack(fill="x")


class InfoCard(tk.Frame):
    """信息卡片"""
    def __init__(self, parent, label, value, **kwargs):
        super().__init__(parent, bg="white", **kwargs)
        tk.Label(self, text=label, font=("微软雅黑", 10), bg="white",
                fg="#666").pack(anchor="w", padx=10, pady=(10, 0))
        tk.Label(self, text=str(value), font=("微软雅黑", 12, "bold"),
                bg="white", fg="#333").pack(anchor="w", padx=10, pady=(0, 10))


# ==================== 登录页面 ====================

class LoginPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="#F0F4F8")

        # 居中容器
        center = tk.Frame(self, bg="#F0F4F8")
        center.place(relx=0.5, rely=0.45, anchor="center")

        # Logo / 标题
        tk.Label(center, text="🏫 校园跑腿系统", font=("微软雅黑", 26, "bold"),
                bg="#F0F4F8", fg="#2C3E50").pack(pady=(0, 5))
        tk.Label(center, text="便捷校园 · 轻松跑腿", font=("微软雅黑", 11),
                bg="#F0F4F8", fg="#7F8C8D").pack(pady=(0, 30))

        # 登录卡片
        card = tk.Frame(center, bg="white", padx=40, pady=30,
                       highlightbackground="#E0E0E0", highlightthickness=1)
        card.pack()

        tk.Label(card, text="用户登录", font=("微软雅黑", 16, "bold"),
                bg="white", fg="#2C3E50").pack(pady=(0, 20))

        # 用户名
        tk.Label(card, text="用户名", font=("微软雅黑", 10),
                bg="white", fg="#555").pack(anchor="w")
        self.entry_username = tk.Entry(card, font=("微软雅黑", 12), width=25,
                                       relief="solid", bd=1)
        self.entry_username.pack(pady=(2, 10))
        self.entry_username.insert(0, "admin")  # 默认填充

        # 密码
        tk.Label(card, text="密码", font=("微软雅黑", 10),
                bg="white", fg="#555").pack(anchor="w")
        self.entry_password = tk.Entry(card, font=("微软雅黑", 12), width=25,
                                       show="*", relief="solid", bd=1)
        self.entry_password.pack(pady=(2, 10))
        self.entry_password.insert(0, "123456")
        self.entry_password.bind("<Return>", lambda e: self.login())

        # 登录按钮
        tk.Button(card, text="登 录", font=("微软雅黑", 12, "bold"),
                 bg="#4A90D9", fg="white", bd=0, padx=20, pady=5,
                 activebackground="#357ABD",
                 command=self.login).pack(pady=(5, 15), fill="x")

        # 注册入口
        reg_frame = tk.Frame(card, bg="white")
        reg_frame.pack()
        tk.Label(reg_frame, text="还没有账号？", font=("微软雅黑", 9),
                bg="white", fg="#999").pack(side="left")
        reg_btn = tk.Label(reg_frame, text="立即注册", font=("微软雅黑", 9, "bold"),
                          bg="white", fg="#4A90D9", cursor="hand2")
        reg_btn.pack(side="left")
        reg_btn.bind("<Button-1>", lambda e: app.show_page("RegisterPage"))

        # 快速登录提示
        tk.Label(center, text="💡 快速体验：admin/123456 | zhangsan/123456 | lisi/123456",
                font=("微软雅黑", 9), bg="#F0F4F8", fg="#AAA").pack(pady=(20, 0))

    def login(self):
        global current_user
        username = self.entry_username.get().strip()
        password = self.entry_password.get().strip()

        if not username or not password:
            messagebox.showwarning("提示", "请输入用户名和密码")
            return

        ok, result = db.login(username, password)
        if not ok:
            messagebox.showerror("登录失败", result)
            return

        current_user = result
        messagebox.showinfo("登录成功", f"欢迎回来，{result['name']}！")

        role = result["role"]
        if role == "admin":
            self.app.show_page("AdminPage")
        elif role == "delivery":
            self.app.show_page("DeliveryHomePage")
        else:
            self.app.show_page("RequesterHomePage")


class RegisterPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="#F0F4F8")

        HeaderFrame(self, app, "注册新账号", show_back=True,
                   back_callback=lambda: app.show_page("LoginPage"))

        center = tk.Frame(self, bg="#F0F4F8")
        center.pack(expand=True)

        card = tk.Frame(center, bg="white", padx=40, pady=25,
                       highlightbackground="#E0E0E0", highlightthickness=1)
        card.pack()

        tk.Label(card, text="注册", font=("微软雅黑", 16, "bold"),
                bg="white", fg="#2C3E50").pack(pady=(0, 20))

        fields = [
            ("用户名", "entry_username"),
            ("密码", "entry_password", "*"),
            ("真实姓名", "entry_name"),
            ("手机号", "entry_phone"),
            ("学号（可选）", "entry_student_id"),
        ]
        self.entries = {}
        for field in fields:
            label = field[0]
            key = field[1]
            show = field[2] if len(field) > 2 else None
            tk.Label(card, text=label, font=("微软雅黑", 10),
                    bg="white", fg="#555").pack(anchor="w", pady=(5, 0))
            entry = tk.Entry(card, font=("微软雅黑", 11), width=25,
                            relief="solid", bd=1, show=show or "")
            entry.pack(pady=(2, 5))
            self.entries[key] = entry

        # 角色选择
        tk.Label(card, text="注册身份", font=("微软雅黑", 10),
                bg="white", fg="#555").pack(anchor="w", pady=(5, 0))
        self.role_var = tk.StringVar(value="requester")
        role_frame = tk.Frame(card, bg="white")
        role_frame.pack(pady=(5, 15))
        for val, text in [("requester", "需求方（发布任务）"),
                          ("delivery", "配送员（接单跑腿）")]:
            tk.Radiobutton(role_frame, text=text, variable=self.role_var,
                          value=val, bg="white", font=("微软雅黑", 10),
                          activebackground="white").pack(anchor="w")

        # 注册按钮
        tk.Button(card, text="注 册", font=("微软雅黑", 12, "bold"),
                 bg="#4A90D9", fg="white", bd=0, padx=20, pady=5,
                 activebackground="#357ABD",
                 command=self.register).pack(pady=(5, 10), fill="x")

    def register(self):
        data = {k: v.get().strip() for k, v in self.entries.items()}
        if not data["entry_username"] or not data["entry_password"] or not data["entry_name"]:
            messagebox.showwarning("提示", "请填写必填项（用户名、密码、姓名）")
            return

        ok, msg = db.register(
            username=data["entry_username"],
            password=data["entry_password"],
            role=self.role_var.get(),
            name=data["entry_name"],
            phone=data["entry_phone"],
            student_id=data["entry_student_id"]
        )
        if ok:
            messagebox.showinfo("成功", "注册成功！请登录。")
            self.app.show_page("LoginPage")
        else:
            messagebox.showerror("注册失败", msg)


# ==================== 需求方页面 ====================

class RequesterHomePage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="#F0F4F8")

        HeaderFrame(self, app, "校园跑腿 - 需求端")

        # 功能按钮区
        btn_frame = tk.Frame(self, bg="#F0F4F8")
        btn_frame.pack(fill="x", padx=20, pady=(20, 10))

        btns = [
            ("📦 发布订单", self.new_order, "#4A90D9"),
            ("📋 我的订单", self.my_orders, "#27AE60"),
            ("⭐ 评价配送", self.my_reviews, "#E67E22"),
            ("👤 个人中心", self.profile, "#8E44AD"),
        ]
        for text, cmd, color in btns:
            btn = tk.Button(btn_frame, text=text, font=("微软雅黑", 11, "bold"),
                          bg=color, fg="white", bd=0, padx=15, pady=10,
                          activebackground=color, command=cmd)
            btn.pack(side="left", expand=True, fill="x", padx=5)

        # 最近订单
        tk.Label(self, text="我的订单", font=("微软雅黑", 13, "bold"),
                bg="#F0F4F8", fg="#2C3E50").pack(anchor="w", padx=20, pady=(15, 5))

        self.list_frame = tk.Frame(self, bg="#F0F4F8")
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def on_show(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        orders = db.get_orders_by_user(current_user["username"])
        if not orders:
            tk.Label(self.list_frame, text="暂无订单，点击上方「发布订单」开始",
                    font=("微软雅黑", 11), bg="#F0F4F8", fg="#AAA").pack(pady=40)
            return

        for o in sorted(orders, key=lambda x: x["created_at"], reverse=True)[:10]:
            self._create_order_card(o)

    def _create_order_card(self, o):
        status_colors = {"待接单": "#E67E22", "配送中": "#3498DB",
                        "已完成": "#27AE60", "已取消": "#95A5A6"}
        sc = status_colors.get(o["status"], "#666")

        card = tk.Frame(self.list_frame, bg="white", padx=15, pady=10,
                       highlightbackground="#E8E8E8", highlightthickness=1)
        card.pack(fill="x", pady=3)

        # 标题行
        row1 = tk.Frame(card, bg="white")
        row1.pack(fill="x")
        tk.Label(row1, text=f"[{o['type']}] {o['details'][:20]}...",
                font=("微软雅黑", 11, "bold"), bg="white", fg="#333"
                ).pack(side="left")
        tk.Label(row1, text=o["status"], font=("微软雅黑", 10),
                bg=sc, fg="white", padx=8, pady=1).pack(side="right")

        # 信息行
        row2 = tk.Frame(card, bg="white")
        row2.pack(fill="x", pady=(5, 0))
        tk.Label(row2, text=f"¥{o['reward']} | {o['created_at']} | {o['pickup']} → {o['dropoff']}",
                font=("微软雅黑", 9), bg="white", fg="#888").pack(side="left")

        # 操作按钮
        if o["status"] == "待接单":
            tk.Button(row2, text="取消", font=("微软雅黑", 9),
                     bg="#E74C3C", fg="white", bd=0, padx=8,
                     command=lambda oid=o["id"]: self.cancel(oid)).pack(side="right", padx=2)
        elif o["status"] == "已完成" and not db.review_exists(o["id"]):
            tk.Button(row2, text="评价", font=("微软雅黑", 9),
                     bg="#E67E22", fg="white", bd=0, padx=8,
                     command=lambda oid=o["id"]: self.review(oid)).pack(side="right", padx=2)

    def cancel(self, oid):
        ok, msg = db.cancel_order(oid)
        messagebox.showinfo("结果", msg)
        self.on_show()

    def review(self, oid):
        self.app.show_page("ReviewPage", order_id=oid)

    def new_order(self):
        self.app.show_page("NewOrderPage")


    def my_orders(self):
        self.app.show_page("RequesterOrderListPage")

    def my_reviews(self):
        self.app.show_page("ReviewListPage")

    def profile(self):
        self.app.show_page("ProfilePage")


class NewOrderPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="#F0F4F8")

        HeaderFrame(self, app, "发布新订单", show_back=True,
                   back_callback=lambda: app.show_page("RequesterHomePage"))

        center = tk.Frame(self, bg="#F0F4F8")
        center.pack(expand=True, fill="both", padx=40, pady=20)

        # 使用 Canvas + Scrollbar 支持滚动
        canvas = tk.Canvas(center, bg="#F0F4F8", highlightthickness=0)
        scrollbar = tk.Scrollbar(center, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white",
                               highlightbackground="#E0E0E0", highlightthickness=1)
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(
                           scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 绑定鼠标滚轮
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        self._unbind = lambda: canvas.unbind_all("<MouseWheel>")

        inner = scroll_frame

        tk.Label(inner, text="📝 填写订单信息", font=("微软雅黑", 16, "bold"),
                bg="white", fg="#2C3E50").pack(pady=(20, 20))

        # 订单类型
        tk.Label(inner, text="订单类型 *", font=("微软雅黑", 10),
                bg="white", fg="#555").pack(anchor="w", padx=40)
        self.type_var = tk.StringVar(value="快递代取")
        type_frame = tk.Frame(inner, bg="white")
        type_frame.pack(pady=5)
        for t in ["快递代取", "外卖代送", "文件代送", "其他"]:
            tk.Radiobutton(type_frame, text=t, variable=self.type_var,
                          value=t, bg="white", font=("微软雅黑", 10),
                          activebackground="white").pack(side="left", padx=10)

        # 详情
        def make_entry(label, key, width=30):
            tk.Label(inner, text=label, font=("微软雅黑", 10),
                    bg="white", fg="#555").pack(anchor="w", padx=40, pady=(10, 0))
            e = tk.Entry(inner, font=("微软雅黑", 11), width=width,
                        relief="solid", bd=1)
            e.pack(pady=(2, 0))
            self.entries[key] = e

        self.entries = {}
        make_entry("详细描述（如快递单号、商家名称等）*", "details", 40)
        make_entry("取件地点 *", "pickup", 30)
        make_entry("送达地点 *", "dropoff", 30)
        make_entry("跑腿费（元）*", "reward", 15)
        make_entry("备注（可选）", "note", 40)

        # 提交按钮
        tk.Button(inner, text="发布订单", font=("微软雅黑", 13, "bold"),
                 bg="#4A90D9", fg="white", bd=0, padx=40, pady=8,
                 activebackground="#357ABD",
                 command=self.submit).pack(pady=(25, 30))

    def submit(self):
        data = {k: v.get().strip() for k, v in self.entries.items()}
        if not data.get("details") or not data.get("pickup") or not data.get("dropoff"):
            messagebox.showwarning("提示", "请填写必填项（描述、取件地点、送达地点）")
            return

        try:
            reward = float(data.get("reward", 0))
            if reward < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("提示", "跑腿费请输入有效数字")
            return

        oid = db.create_order(
            requester=current_user["username"],
            order_type=self.type_var.get(),
            details=data["details"],
            pickup_location=data["pickup"],
            dropoff_location=data["dropoff"],
            reward=reward,
            note=data["note"]
        )
        messagebox.showinfo("成功", f"订单发布成功！订单号：{oid}")
        self.app.show_page("RequesterHomePage")

    def destroy(self):
        if hasattr(self, "_unbind"):
            self._unbind()
        super().destroy()


class RequesterOrderListPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="#F0F4F8")
        HeaderFrame(self, app, "我的订单", show_back=True,
                   back_callback=lambda: app.show_page("RequesterHomePage"))

        self.list_frame = tk.Frame(self, bg="#F0F4F8")
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def on_show(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        orders = db.get_orders_by_user(current_user["username"])
        if not orders:
            tk.Label(self.list_frame, text="暂无订单记录",
                    font=("微软雅黑", 12), bg="#F0F4F8", fg="#AAA").pack(pady=40)
            return

        # 状态筛选
        filter_frame = tk.Frame(self.list_frame, bg="#F0F4F8")
        filter_frame.pack(fill="x", pady=(0, 10))

        def filter_orders(status):
            for w in self.list_frame.winfo_children():
                w.destroy()
            filter_frame.pack(fill="x", pady=(0, 10))
            filtered = [o for o in orders if status == "全部" or o["status"] == status]
            if not filtered:
                tk.Label(self.list_frame, text="暂无该状态订单",
                        font=("微软雅黑", 12), bg="#F0F4F8", fg="#AAA").pack(pady=40)
                return
            for o in sorted(filtered, key=lambda x: x["created_at"], reverse=True):
                self._order_card(o)

        for s in ["全部", "待接单", "配送中", "已完成", "已取消"]:
            btn = tk.Button(filter_frame, text=s, font=("微软雅黑", 9),
                          bg="#ECF0F1", fg="#333", bd=1, padx=10,
                          command=lambda st=s: filter_orders(st))
            btn.pack(side="left", padx=2)

        # 显示全部
        for o in sorted(orders, key=lambda x: x["created_at"], reverse=True):
            self._order_card(o)

    def _order_card(self, o):
        status_colors = {"待接单": "#E67E22", "配送中": "#3498DB",
                        "已完成": "#27AE60", "已取消": "#95A5A6"}
        sc = status_colors.get(o["status"], "#666")

        card = tk.Frame(self.list_frame, bg="white", padx=15, pady=10,
                       highlightbackground="#E8E8E8", highlightthickness=1)
        card.pack(fill="x", pady=3)

        row1 = tk.Frame(card, bg="white")
        row1.pack(fill="x")
        tk.Label(row1, text=f"[{o['type']}] {o['details'][:25]}...",
                font=("微软雅黑", 11, "bold"), bg="white", fg="#333").pack(side="left")
        tk.Label(row1, text=o["status"], font=("微软雅黑", 10),
                bg=sc, fg="white", padx=8, pady=1).pack(side="right")

        row2 = tk.Frame(card, bg="white")
        row2.pack(fill="x", pady=(5, 0))
        tk.Label(row2, text=f"¥{o['reward']} | {o['created_at']} | {o['pickup']} → {o['dropoff']}",
                font=("微软雅黑", 9), bg="white", fg="#888").pack(side="left")

        if o["status"] == "配送中":
            dp = o.get("delivery_person")
            if dp:
                u = db.get_user(dp)
                tk.Label(row2, text=f"配送员: {u['name']}" if u else "",
                        font=("微软雅黑", 9), bg="white", fg="#4A90D9").pack(side="right", padx=5)
        elif o["status"] == "已完成" and not db.review_exists(o["id"]):
            tk.Button(row2, text="评价", font=("微软雅黑", 9),
                     bg="#E67E22", fg="white", bd=0, padx=8,
                     command=lambda oid=o["id"]: self.app.show_page("ReviewPage", order_id=oid)
                     ).pack(side="right", padx=2)


# ==================== 配送员页面 ====================

class DeliveryHomePage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="#F0F4F8")

        HeaderFrame(self, app, "校园跑腿 - 配送端")

        # 配送员信息
        info_frame = tk.Frame(self, bg="white", padx=20, pady=10,
                            highlightbackground="#E8E8E8", highlightthickness=1)
        info_frame.pack(fill="x", padx=20, pady=(15, 10))

        tk.Label(info_frame, text=f"配送员: {current_user['name']}",
                font=("微软雅黑", 12, "bold"), bg="white", fg="#333").pack(side="left")
        tk.Label(info_frame, text=f"⭐ {current_user.get('rating', 5.0)}  ",
                font=("微软雅黑", 11), bg="white", fg="#E67E22").pack(side="left", padx=20)
        tk.Label(info_frame, text=f"已完成: {current_user.get('completed', 0)} 单",
                font=("微软雅黑", 11), bg="white", fg="#27AE60").pack(side="left")

        # 功能按钮
        btn_frame = tk.Frame(self, bg="#F0F4F8")
        btn_frame.pack(fill="x", padx=20, pady=10)

        btns = [
            ("📋 浏览订单", self.browse_orders, "#4A90D9"),
            ("🚚 我的配送", self.my_deliveries, "#27AE60"),
            ("💰 我的收入", self.my_income, "#E67E22"),
        ]
        for text, cmd, color in btns:
            btn = tk.Button(btn_frame, text=text, font=("微软雅黑", 11, "bold"),
                          bg=color, fg="white", bd=0, padx=15, pady=10,
                          activebackground=color, command=cmd)
            btn.pack(side="left", expand=True, fill="x", padx=5)

        # 待接单列表
        tk.Label(self, text="📌 待接订单", font=("微软雅黑", 13, "bold"),
                bg="#F0F4F8", fg="#2C3E50").pack(anchor="w", padx=20, pady=(15, 5))

        self.list_frame = tk.Frame(self, bg="#F0F4F8")
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

    def on_show(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        orders = db.get_available_orders()
        if not orders:
            tk.Label(self.list_frame, text="暂无待接订单，请稍后再来",
                    font=("微软雅黑", 12), bg="#F0F4F8", fg="#AAA").pack(pady=40)
            return

        for o in sorted(orders, key=lambda x: x["reward"], reverse=True):
            self._order_card(o)

    def _order_card(self, o):
        card = tk.Frame(self.list_frame, bg="white", padx=15, pady=10,
                       highlightbackground="#E8E8E8", highlightthickness=1)
        card.pack(fill="x", pady=3)

        row1 = tk.Frame(card, bg="white")
        row1.pack(fill="x")
        tk.Label(row1, text=f"[{o['type']}] {o['details'][:20]}...",
                font=("微软雅黑", 11, "bold"), bg="white", fg="#333").pack(side="left")
        tk.Label(row1, text=f"¥{o['reward']}", font=("微软雅黑", 12, "bold"),
                bg="white", fg="#E74C3C").pack(side="right")

        row2 = tk.Frame(card, bg="white")
        row2.pack(fill="x", pady=(3, 0))
        tk.Label(row2, text=f"📍 {o['pickup']} → {o['dropoff']}  |  {o['created_at']}",
                font=("微软雅黑", 9), bg="white", fg="#888").pack(side="left")

        row3 = tk.Frame(card, bg="white")
        row3.pack(fill="x", pady=(5, 0))

        if o.get("note"):
            tk.Label(row3, text=f"备注: {o['note']}", font=("微软雅黑", 9),
                    bg="white", fg="#AAA").pack(side="left")

        tk.Button(row3, text="接单", font=("微软雅黑", 10, "bold"),
                 bg="#27AE60", fg="white", bd=0, padx=15,
                 command=lambda oid=o["id"]: self.accept(oid)).pack(side="right")

    def accept(self, oid):
        ok, msg = db.accept_order(oid, current_user["username"])
        if ok:
            messagebox.showinfo("成功", "接单成功！请尽快前往取件。")
        else:
            messagebox.showerror("失败", msg)
        self.on_show()

    def browse_orders(self):
        self.app.show_page("DeliveryBrowsePage")

    def my_deliveries(self):
        self.app.show_page("DeliveryOrderListPage")

    def my_income(self):
        self.app.show_page("DeliveryIncomePage")


class DeliveryBrowsePage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="#F0F4F8")
        HeaderFrame(self, app, "浏览订单", show_back=True,
                   back_callback=lambda: app.show_page("DeliveryHomePage"))

        self.list_frame = tk.Frame(self, bg="#F0F4F8")
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def on_show(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        orders = db.get_available_orders()
        if not orders:
            tk.Label(self.list_frame, text="暂无待接订单",
                    font=("微软雅黑", 12), bg="#F0F4F8", fg="#AAA").pack(pady=40)
            return

        for o in sorted(orders, key=lambda x: x["reward"], reverse=True):
            self._order_card(o)

    def _order_card(self, o):
        card = tk.Frame(self.list_frame, bg="white", padx=15, pady=10,
                       highlightbackground="#E8E8E8", highlightthickness=1)
        card.pack(fill="x", pady=3)

        row1 = tk.Frame(card, bg="white")
        row1.pack(fill="x")
        tk.Label(row1, text=f"[{o['type']}] {o['details'][:20]}...",
                font=("微软雅黑", 11, "bold"), bg="white", fg="#333").pack(side="left")

        row2 = tk.Frame(card, bg="white")
        row2.pack(fill="x", pady=(3, 0))
        tk.Label(row2, text=f"📍 {o['pickup']} → {o['dropoff']}",
                font=("微软雅黑", 9), bg="white", fg="#888").pack(side="left")

        row3 = tk.Frame(card, bg="white")
        row3.pack(fill="x", pady=(5, 0))
        tk.Label(row3, text=f"跑腿费: ¥{o['reward']}  发布时间: {o['created_at']}",
                font=("微软雅黑", 10), bg="white", fg="#E74C3C").pack(side="left")

        if o.get("note"):
            tk.Label(row3, text=f" | 备注: {o['note']}",
                    font=("微软雅黑", 9), bg="white", fg="#AAA").pack(side="left", padx=5)

        tk.Button(row3, text="接单", font=("微软雅黑", 10, "bold"),
                 bg="#27AE60", fg="white", bd=0, padx=15,
                 command=lambda oid=o["id"]: self.accept(oid)).pack(side="right")

    def accept(self, oid):
        ok, msg = db.accept_order(oid, current_user["username"])
        if ok:
            messagebox.showinfo("成功", "接单成功！")
            self.app.show_page("DeliveryHomePage")
        else:
            messagebox.showerror("失败", msg)
            self.on_show()


class DeliveryOrderListPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="#F0F4F8")
        HeaderFrame(self, app, "我的配送", show_back=True,
                   back_callback=lambda: app.show_page("DeliveryHomePage"))

        self.list_frame = tk.Frame(self, bg="#F0F4F8")
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def on_show(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        orders = db.get_orders_by_delivery(current_user["username"])
        if not orders:
            tk.Label(self.list_frame, text="暂无配送记录",
                    font=("微软雅黑", 12), bg="#F0F4F8", fg="#AAA").pack(pady=40)
            return

        for o in sorted(orders, key=lambda x: x["accepted_at"] or "", reverse=True):
            self._order_card(o)

    def _order_card(self, o):
        status_colors = {"配送中": "#3498DB", "已完成": "#27AE60"}
        sc = status_colors.get(o["status"], "#666")

        card = tk.Frame(self.list_frame, bg="white", padx=15, pady=10,
                       highlightbackground="#E8E8E8", highlightthickness=1)
        card.pack(fill="x", pady=3)

        row1 = tk.Frame(card, bg="white")
        row1.pack(fill="x")
        tk.Label(row1, text=f"[{o['type']}] {o['details'][:20]}...",
                font=("微软雅黑", 11, "bold"), bg="white", fg="#333").pack(side="left")
        tk.Label(row1, text=o["status"], font=("微软雅黑", 10),
                bg=sc, fg="white", padx=8, pady=1).pack(side="right")

        row2 = tk.Frame(card, bg="white")
        row2.pack(fill="x", pady=(3, 0))
        tk.Label(row2, text=f"¥{o['reward']} | {o['pickup']} → {o['dropoff']}",
                font=("微软雅黑", 9), bg="white", fg="#888").pack(side="left")

        row3 = tk.Frame(card, bg="white")
        row3.pack(fill="x", pady=(5, 0))
        requester = db.get_user(o["requester"])
        tk.Label(row3, text=f"需求方: {requester['name'] if requester else '未知'}",
                font=("微软雅黑", 9), bg="white", fg="#555").pack(side="left")

        if o["status"] == "配送中":
            tk.Button(row3, text="确认送达", font=("微软雅黑", 10, "bold"),
                     bg="#27AE60", fg="white", bd=0, padx=12,
                     command=lambda oid=o["id"]: self.complete(oid)).pack(side="right")

    def complete(self, oid):
        ok, msg = db.complete_order(oid)
        if ok:
            messagebox.showinfo("成功", "订单已送达！")
        else:
            messagebox.showerror("失败", msg)
        self.on_show()


class DeliveryIncomePage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="#F0F4F8")
        HeaderFrame(self, app, "我的收入", show_back=True,
                   back_callback=lambda: app.show_page("DeliveryHomePage"))

        content = tk.Frame(self, bg="#F0F4F8")
        content.pack(expand=True, fill="both", padx=40, pady=40)

        # 收入统计卡片
        orders = [o for o in db.get_orders_by_delivery(current_user["username"])
                 if o["status"] == "已完成"]
        total = sum(o["reward"] for o in orders)

        stats = tk.Frame(content, bg="white", padx=30, pady=30,
                        highlightbackground="#E0E0E0", highlightthickness=1)
        stats.pack(fill="x")

        InfoCard(stats, "已完成订单", f"{len(orders)} 单").pack(side="left", expand=True)
        InfoCard(stats, "总收入", f"¥{total:.2f}").pack(side="left", expand=True)
        rating = current_user.get("rating", 5.0)
        InfoCard(stats, "评分", f"⭐ {rating}").pack(side="left", expand=True)

        # 订单明细
        tk.Label(content, text="已完成订单明细", font=("微软雅黑", 12, "bold"),
                bg="#F0F4F8", fg="#333").pack(anchor="w", pady=(20, 10))

        if not orders:
            tk.Label(content, text="暂无完成记录", font=("微软雅黑", 11),
                    bg="#F0F4F8", fg="#AAA").pack(pady=20)
        else:
            for o in orders:
                item = tk.Frame(content, bg="white", padx=15, pady=8,
                              highlightbackground="#E8E8E8", highlightthickness=1)
                item.pack(fill="x", pady=2)
                tk.Label(item, text=f"[{o['type']}] {o['details'][:20]}...",
                        font=("微软雅黑", 10), bg="white", fg="#333").pack(side="left")
                tk.Label(item, text=f"¥{o['reward']}  {o['completed_at']}",
                        font=("微软雅黑", 10), bg="white", fg="#888").pack(side="right")


# ==================== 评价页面 ====================

class ReviewPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="#F0F4F8")
        HeaderFrame(self, app, "评价配送员", show_back=True,
                   back_callback=lambda: app.show_page("RequesterHomePage"))

        self._order_id = None
        content = tk.Frame(self, bg="#F0F4F8")
        content.pack(expand=True, fill="both", padx=40, pady=40)

        card = tk.Frame(content, bg="white", padx=40, pady=30,
                       highlightbackground="#E0E0E0", highlightthickness=1)
        card.pack()

        tk.Label(card, text="⭐ 评分", font=("微软雅黑", 14, "bold"),
                bg="white", fg="#2C3E50").pack(pady=(0, 20))

        self.rating_var = tk.IntVar(value=5)
        rating_frame = tk.Frame(card, bg="white")
        rating_frame.pack(pady=10)
        for i in range(1, 6):
            rb = tk.Radiobutton(rating_frame, text=f"{i}星", variable=self.rating_var,
                              value=i, bg="white", font=("微软雅黑", 11),
                              activebackground="white")
            rb.pack(side="left", padx=5)

        tk.Label(card, text="评价内容", font=("微软雅黑", 10),
                bg="white", fg="#555").pack(anchor="w", pady=(15, 5))
        self.text_comment = tk.Text(card, font=("微软雅黑", 11), width=40, height=5,
                                    relief="solid", bd=1)
        self.text_comment.pack()

        tk.Button(card, text="提交评价", font=("微软雅黑", 12, "bold"),
                 bg="#E67E22", fg="white", bd=0, padx=30, pady=5,
                 activebackground="#D35400",
                 command=self.submit).pack(pady=(20, 10))

    def on_show(self, **kwargs):
        if "order_id" in kwargs:
            self._order_id = kwargs["order_id"]

    def submit(self):
        if not self._order_id:
            messagebox.showwarning("提示", "订单信息缺失")
            return
        comment = self.text_comment.get("1.0", "end-1c").strip()
        db.add_review(self._order_id, self.rating_var.get(), comment)
        messagebox.showinfo("成功", "评价已提交！")
        self.app.show_page("RequesterHomePage")


class ReviewListPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="#F0F4F8")
        HeaderFrame(self, app, "我的评价", show_back=True,
                   back_callback=lambda: app.show_page("RequesterHomePage"))

        self.list_frame = tk.Frame(self, bg="#F0F4F8")
        self.list_frame.pack(fill="both", expand=True, padx=20, pady=20)

    def on_show(self):
        for w in self.list_frame.winfo_children():
            w.destroy()
        reviews = db.get_reviews_by_requester(current_user["username"])
        if not reviews:
            tk.Label(self.list_frame, text="暂无评价记录",
                    font=("微软雅黑", 12), bg="#F0F4F8", fg="#AAA").pack(pady=40)
            return

        for r in reviews:
            o = db.get_order(r["order_id"])
            card = tk.Frame(self.list_frame, bg="white", padx=15, pady=10,
                          highlightbackground="#E8E8E8", highlightthickness=1)
            card.pack(fill="x", pady=3)

            tk.Label(card, text=f"{'⭐' * r['rating']} {r['rating']}分",
                    font=("微软雅黑", 12), bg="white", fg="#E67E22").pack(anchor="w")
            if r["comment"]:
                tk.Label(card, text=f"\"{r['comment']}\"",
                        font=("微软雅黑", 10), bg="white", fg="#555").pack(anchor="w", pady=(3, 0))
            if o:
                tk.Label(card, text=f"订单: {o['type']} | {o['details'][:15]}...",
                        font=("微软雅黑", 9), bg="white", fg="#AAA").pack(anchor="w")


# ==================== 个人中心 ====================

class ProfilePage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="#F0F4F8")
        HeaderFrame(self, app, "个人中心", show_back=True,
                   back_callback=lambda: app.show_page("RequesterHomePage"))

        content = tk.Frame(self, bg="#F0F4F8")
        content.pack(expand=True, fill="both", padx=40, pady=40)

        card = tk.Frame(content, bg="white", padx=40, pady=30,
                       highlightbackground="#E0E0E0", highlightthickness=1)
        card.pack()

        tk.Label(card, text="👤 个人信息", font=("微软雅黑", 16, "bold"),
                bg="white", fg="#2C3E50").pack(pady=(0, 20))

        fields = [
            ("用户名", current_user["username"]),
            ("姓名", current_user["name"]),
            ("手机号", current_user.get("phone", "")),
            ("学号", current_user.get("student_id", "无")),
            ("角色", {"requester": "需求方", "delivery": "配送员", "admin": "管理员"}
             .get(current_user["role"], current_user["role"])),
        ]
        if current_user["role"] == "delivery":
            fields.append(("评分", f"⭐ {current_user.get('rating', 5.0)}"))
            fields.append(("已完成订单", f"{current_user.get('completed', 0)} 单"))

        for label, value in fields:
            row = tk.Frame(card, bg="white")
            row.pack(fill="x", pady=5)
            tk.Label(row, text=label, font=("微软雅黑", 11), bg="white",
                    fg="#888", width=10, anchor="w").pack(side="left")
            tk.Label(row, text=str(value), font=("微软雅黑", 11), bg="white",
                    fg="#333").pack(side="left", padx=10)

        # 退出登录
        tk.Button(card, text="退出登录", font=("微软雅黑", 12, "bold"),
                 bg="#E74C3C", fg="white", bd=0, padx=30, pady=5,
                 activebackground="#C0392B",
                 command=self.logout).pack(pady=(30, 10))

    def logout(self):
        global current_user
        if messagebox.askyesno("确认", "确定要退出登录吗？"):
            current_user = None
            self.app.clear_pages()
            self.app.show_page("LoginPage")


# ==================== 管理员页面 ====================

class AdminPage(tk.Frame):
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.configure(bg="#F0F4F8")

        HeaderFrame(self, app, "系统管理后台")

        # 统计卡片
        stats_frame = tk.Frame(self, bg="#F0F4F8")
        stats_frame.pack(fill="x", padx=20, pady=(15, 10))

        users = db.get_all_users()
        orders = db.get_all_orders()
        stats = [
            ("👥 总用户", len(users), "#4A90D9"),
            ("📦 总订单", len(orders), "#27AE60"),
            ("🔄 进行中", len([o for o in orders if o["status"] == "配送中"]), "#E67E22"),
            ("✅ 已完成", len([o for o in orders if o["status"] == "已完成" ]), "#2C3E50"),
        ]
        for label, value, color in stats:
            s_card = tk.Frame(stats_frame, bg="white", padx=20, pady=15,
                            highlightbackground="#E8E8E8", highlightthickness=1)
            s_card.pack(side="left", expand=True, fill="x", padx=3)
            tk.Label(s_card, text=label, font=("微软雅黑", 10), bg="white",
                    fg="#888").pack()
            tk.Label(s_card, text=str(value), font=("微软雅黑", 18, "bold"),
                    bg="white", fg=color).pack()

        # Tab 切换
        tab_frame = tk.Frame(self, bg="#F0F4F8")
        tab_frame.pack(fill="x", padx=20, pady=(10, 0))

        self.tab_var = tk.StringVar(value="orders")
        self.content_frame = tk.Frame(self, bg="white",
                                     highlightbackground="#E8E8E8",
                                     highlightthickness=1)
        self.content_frame.pack(fill="both", expand=True, padx=20, pady=(10, 20))

        for val, text in [("orders", "订单管理"), ("users", "用户管理")]:
            btn = tk.Button(tab_frame, text=text, font=("微软雅黑", 10),
                          bg="#ECF0F1", fg="#333", bd=1, padx=15,
                          command=lambda v=val: self.switch_tab(v))
            btn.pack(side="left", padx=2)

        self.switch_tab("orders")

    def switch_tab(self, tab):
        self.tab_var.set(tab)
        for w in self.content_frame.winfo_children():
            w.destroy()

        if tab == "orders":
            self._show_orders()
        else:
            self._show_users()

    def _show_orders(self):
        canvas = tk.Canvas(self.content_frame, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(
                           scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        orders = db.get_all_orders()
        if not orders:
            tk.Label(scroll_frame, text="暂无订单记录",
                    font=("微软雅黑", 11), bg="white", fg="#AAA").pack(pady=40)
            return

        # 表头
        header = tk.Frame(scroll_frame, bg="#F8F9FA")
        header.pack(fill="x", padx=10, pady=(10, 0))
        for col, w in [("订单号", 10), ("类型", 8), ("需求方", 8), ("配送员", 8),
                        ("状态", 8), ("金额", 6), ("时间", 14)]:
            tk.Label(header, text=col, font=("微软雅黑", 9, "bold"),
                    bg="#F8F9FA", fg="#555", width=w).pack(side="left")

        for o in sorted(orders, key=lambda x: x["created_at"], reverse=True):
            row = tk.Frame(scroll_frame, bg="white")
            row.pack(fill="x", padx=10, pady=1)
            dp_name = ""
            if o["delivery_person"]:
                u = db.get_user(o["delivery_person"])
                dp_name = u["name"] if u else o["delivery_person"]
            requester = db.get_user(o["requester"])
            rq_name = requester["name"] if requester else o["requester"]

            status_colors = {"待接单": "#E67E22", "配送中": "#3498DB",
                            "已完成": "#27AE60", "已取消": "#95A5A6"}
            sc = status_colors.get(o["status"], "#666")

            tk.Label(row, text=o["id"], font=("微软雅黑", 9), bg="white",
                    fg="#333", width=10).pack(side="left")
            tk.Label(row, text=o["type"], font=("微软雅黑", 9), bg="white",
                    fg="#333", width=8).pack(side="left")
            tk.Label(row, text=rq_name, font=("微软雅黑", 9), bg="white",
                    fg="#333", width=8).pack(side="left")
            tk.Label(row, text=dp_name or "-", font=("微软雅黑", 9), bg="white",
                    fg="#333", width=8).pack(side="left")
            tk.Label(row, text=o["status"], font=("微软雅黑", 9), bg=sc,
                    fg="white", width=8).pack(side="left")
            tk.Label(row, text=f"¥{o['reward']}", font=("微软雅黑", 9), bg="white",
                    fg="#E74C3C", width=6).pack(side="left")
            tk.Label(row, text=o["created_at"], font=("微软雅黑", 9), bg="white",
                    fg="#888", width=14).pack(side="left")

    def _show_users(self):
        canvas = tk.Canvas(self.content_frame, bg="white", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.content_frame, orient="vertical", command=canvas.yview)
        scroll_frame = tk.Frame(canvas, bg="white")
        scroll_frame.bind("<Configure>", lambda e: canvas.configure(
                           scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        users = db.get_all_users()
        role_map = {"requester": "需求方", "delivery": "配送员", "admin": "管理员"}

        header = tk.Frame(scroll_frame, bg="#F8F9FA")
        header.pack(fill="x", padx=10, pady=(10, 0))
        for col, w in [("用户名", 12), ("姓名", 10), ("角色", 10),
                        ("手机号", 12), ("学号", 10)]:
            tk.Label(header, text=col, font=("微软雅黑", 9, "bold"),
                    bg="#F8F9FA", fg="#555", width=w).pack(side="left")

        for u in users:
            row = tk.Frame(scroll_frame, bg="white")
            row.pack(fill="x", padx=10, pady=1)
            tk.Label(row, text=u["username"], font=("微软雅黑", 9), bg="white",
                    fg="#333", width=12).pack(side="left")
            tk.Label(row, text=u["name"], font=("微软雅黑", 9), bg="white",
                    fg="#333", width=10).pack(side="left")
            tk.Label(row, text=role_map.get(u["role"], u["role"]),
                    font=("微软雅黑", 9), bg="white", fg="#333", width=10).pack(side="left")
            tk.Label(row, text=u.get("phone", ""), font=("微软雅黑", 9), bg="white",
                    fg="#333", width=12).pack(side="left")
            tk.Label(row, text=u.get("student_id", ""), font=("微软雅黑", 9), bg="white",
                    fg="#333", width=10).pack(side="left")


# ==================== 启动入口 ====================

if __name__ == "__main__":
    app = App()
    app.mainloop()
