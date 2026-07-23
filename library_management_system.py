#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
图书管理系统 (Library Management System)
=====================================
一个完整的命令行图书管理系统，包含：
- 图书管理（增删改查）
- 用户管理（注册、查询）
- 借阅系统（借书、还书、记录）
- 数据持久化（JSON）
- 数据统计（分类统计、热门排行、逾期检测）
- 操作日志（装饰器实现）
"""

import json
import os
import re
import csv
from datetime import datetime, timedelta
from functools import wraps
from collections import Counter, defaultdict

# ============================================================
# 一、自定义异常类
# ============================================================

class LibraryException(Exception):
    """图书管理系统基础异常"""
    pass


class BookNotFoundError(LibraryException):
    """图书不存在"""
    pass


class BookAlreadyExistsError(LibraryException):
    """图书已存在（ISBN重复）"""
    pass


class UserNotFoundError(LibraryException):
    """用户不存在"""
    pass


class UserAlreadyExistsError(LibraryException):
    """用户已存在"""
    pass


class InsufficientStockError(LibraryException):
    """库存不足"""
    pass


class BorrowLimitExceededError(LibraryException):
    """超出借阅上限"""
    pass


class BookNotBorrowedError(LibraryException):
    """用户未借阅该图书"""
    pass


class ISBNFormatError(LibraryException):
    """ISBN格式错误"""
    pass


# ============================================================
# 二、操作日志装饰器
# ============================================================

def log_operation(func):
    """
    操作日志装饰器
    记录每次操作的时间、函数名、参数和结果
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        func_name = func.__name__

        # 获取self中的service名称（如果存在）
        instance_name = args[0].__class__.__name__ if args else "Unknown"

        try:
            result = func(*args, **kwargs)
            # 简化结果输出
            if isinstance(result, bool):
                status = "成功" if result else "失败"
            elif result is None:
                status = "完成"
            else:
                status = "成功"

            log_msg = f"[{timestamp}] [{instance_name}] 操作: {func_name}, 结果: {status}"
            print(f"  📋 {log_msg}")

            # 写入日志文件
            with open("library.log", "a", encoding="utf-8") as f:
                f.write(log_msg + "\n")

            return result
        except LibraryException as e:
            status = f"失败 - {str(e)}"
            log_msg = f"[{timestamp}] [{instance_name}] 操作: {func_name}, 结果: {status}"
            print(f"  ❌ {log_msg}")
            with open("library.log", "a", encoding="utf-8") as f:
                f.write(log_msg + "\n")
            raise

    return wrapper


# ============================================================
# 三、实体类
# ============================================================

class Book:
    """
    图书实体类

    Attributes:
        isbn: 国际标准书号（唯一标识）
        title: 书名
        author: 作者
        publisher: 出版社
        category: 分类
        stock: 总库存数量
        borrowed: 已借出数量
    """

    def __init__(self, isbn, title, author, publisher, category, stock):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.publisher = publisher
        self.category = category
        self.stock = stock          # 总库存
        self.borrowed = 0           # 已借出数量

    @property
    def available(self):
        """可用库存 = 总库存 - 已借出"""
        return self.stock - self.borrowed

    def to_dict(self):
        """序列化为字典"""
        return {
            "isbn": self.isbn,
            "title": self.title,
            "author": self.author,
            "publisher": self.publisher,
            "category": self.category,
            "stock": self.stock,
            "borrowed": self.borrowed
        }

    @classmethod
    def from_dict(cls, data):
        """从字典反序列化"""
        book = cls(
            isbn=data["isbn"],
            title=data["title"],
            author=data["author"],
            publisher=data["publisher"],
            category=data["category"],
            stock=data["stock"]
        )
        book.borrowed = data.get("borrowed", 0)
        return book

    def __str__(self):
        return (f"《{self.title}》| 作者: {self.author} | "
                f"ISBN: {self.isbn} | 分类: {self.category} | "
                f"库存: {self.available}/{self.stock}")

    def __repr__(self):
        return f"Book({self.isbn}, {self.title})"


class User:
    """
    用户实体类

    Attributes:
        user_id: 用户唯一标识
        name: 用户姓名
        register_date: 注册日期
        borrowed_books: 当前借阅的图书ISBN列表
        borrow_history: 借阅历史记录ID列表
    """

    MAX_BORROW = 5  # 最大借阅数量

    def __init__(self, user_id, name):
        self.user_id = user_id
        self.name = name
        self.register_date = datetime.now().strftime("%Y-%m-%d")
        self.borrowed_books = []    # 当前借阅的ISBN列表
        self.borrow_history = []    # 历史借阅记录ID列表

    @property
    def current_borrow_count(self):
        """当前借阅数量"""
        return len(self.borrowed_books)

    @property
    def can_borrow(self):
        """是否还能借书"""
        return self.current_borrow_count < self.MAX_BORROW

    def to_dict(self):
        """序列化为字典"""
        return {
            "user_id": self.user_id,
            "name": self.name,
            "register_date": self.register_date,
            "borrowed_books": self.borrowed_books,
            "borrow_history": self.borrow_history
        }

    @classmethod
    def from_dict(cls, data):
        """从字典反序列化"""
        user = cls(
            user_id=data["user_id"],
            name=data["name"]
        )
        user.register_date = data.get("register_date", datetime.now().strftime("%Y-%m-%d"))
        user.borrowed_books = data.get("borrowed_books", [])
        user.borrow_history = data.get("borrow_history", [])
        return user

    def __str__(self):
        return (f"用户: {self.name}({self.user_id}) | "
                f"注册日期: {self.register_date} | "
                f"当前借阅: {self.current_borrow_count}/{self.MAX_BORROW}")

    def __repr__(self):
        return f"User({self.user_id}, {self.name})"


class BorrowRecord:
    """
    借阅记录实体类

    Attributes:
        record_id: 记录唯一标识
        user_id: 借阅用户ID
        isbn: 借阅图书ISBN
        borrow_date: 借阅日期
        due_date: 应还日期（借阅后30天）
        return_date: 实际归还日期（未还为None）
        status: 状态（"借阅中" / "已归还"）
    """

    _id_counter = 0

    def __init__(self, user_id, isbn, borrow_date=None):
        BorrowRecord._id_counter += 1
        self.record_id = f"R{BorrowRecord._id_counter:06d}"
        self.user_id = user_id
        self.isbn = isbn
        self.borrow_date = borrow_date or datetime.now().strftime("%Y-%m-%d")
        self.due_date = (datetime.strptime(self.borrow_date, "%Y-%m-%d") + 
                         timedelta(days=30)).strftime("%Y-%m-%d")
        self.return_date = None
        self.status = "借阅中"

    @property
    def is_overdue(self):
        """是否逾期"""
        if self.status == "已归还":
            return False
        today = datetime.now()
        due = datetime.strptime(self.due_date, "%Y-%m-%d")
        return today > due

    @property
    def overdue_days(self):
        """逾期天数"""
        if not self.is_overdue:
            return 0
        today = datetime.now()
        due = datetime.strptime(self.due_date, "%Y-%m-%d")
        return (today - due).days

    def return_book(self):
        """归还图书"""
        self.return_date = datetime.now().strftime("%Y-%m-%d")
        self.status = "已归还"

    def to_dict(self):
        """序列化为字典"""
        return {
            "record_id": self.record_id,
            "user_id": self.user_id,
            "isbn": self.isbn,
            "borrow_date": self.borrow_date,
            "due_date": self.due_date,
            "return_date": self.return_date,
            "status": self.status
        }

    @classmethod
    def from_dict(cls, data):
        """从字典反序列化"""
        record = cls.__new__(cls)
        record.record_id = data["record_id"]
        record.user_id = data["user_id"]
        record.isbn = data["isbn"]
        record.borrow_date = data["borrow_date"]
        record.due_date = data["due_date"]
        record.return_date = data["return_date"]
        record.status = data["status"]

        # 更新计数器
        num = int(data["record_id"][1:])
        if num > BorrowRecord._id_counter:
            BorrowRecord._id_counter = num
        return record

    def __str__(self):
        base = (f"[{self.record_id}] 用户: {self.user_id} | 图书: {self.isbn} | "
                f"借阅: {self.borrow_date} | 应还: {self.due_date} | 状态: {self.status}")
        if self.is_overdue:
            base += f" | ⚠️ 已逾期 {self.overdue_days} 天"
        return base

    def __repr__(self):
        return f"BorrowRecord({self.record_id}, {self.user_id}, {self.isbn})"


# ============================================================
# 四、数据持久化层
# ============================================================

class DataStore:
    """
    数据持久化层
    负责所有数据的JSON序列化和反序列化
    """

    def __init__(self, filepath="library_data.json"):
        self.filepath = filepath

    def save(self, books, users, records):
        """
        保存所有数据到JSON文件

        Args:
            books: 图书字典 {isbn: Book}
            users: 用户字典 {user_id: User}
            records: 借阅记录列表 [BorrowRecord]
        """
        data = {
            "books": {isbn: book.to_dict() for isbn, book in books.items()},
            "users": {uid: user.to_dict() for uid, user in users.items()},
            "records": [record.to_dict() for record in records]
        }

        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"  💾 数据已保存到 {self.filepath}")

    def load(self):
        """
        从JSON文件加载数据

        Returns:
            tuple: (books_dict, users_dict, records_list)
        """
        if not os.path.exists(self.filepath):
            print(f"  📂 数据文件不存在，创建新数据库")
            return {}, {}, []

        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            books = {isbn: Book.from_dict(b) for isbn, b in data.get("books", {}).items()}
            users = {uid: User.from_dict(u) for uid, u in data.get("users", {}).items()}
            records = [BorrowRecord.from_dict(r) for r in data.get("records", [])]

            print(f"  📂 数据加载成功: {len(books)} 本图书, {len(users)} 个用户, {len(records)} 条记录")
            return books, users, records

        except (json.JSONDecodeError, KeyError) as e:
            print(f"  ⚠️ 数据文件损坏: {e}，创建新数据库")
            return {}, {}, []


# ============================================================
# 五、业务逻辑层（核心服务）
# ============================================================

class LibraryService:
    """
    图书管理系统核心业务逻辑层
    封装所有业务操作，处理异常，调用数据持久化
    """

    def __init__(self):
        self.data_store = DataStore()
        self.books = {}      # {isbn: Book}
        self.users = {}      # {user_id: User}
        self.records = []    # [BorrowRecord]
        self._load_data()

    def _load_data(self):
        """加载数据"""
        self.books, self.users, self.records = self.data_store.load()

    def _save_data(self):
        """保存数据"""
        self.data_store.save(self.books, self.users, self.records)

    # ---------- ISBN 验证 ----------

    @staticmethod
    def validate_isbn(isbn):
        """
        验证ISBN格式（支持ISBN-10和ISBN-13）

        Args:
            isbn: 待验证的ISBN字符串

        Raises:
            ISBNFormatError: 格式不正确时抛出
        """
        # 移除连字符和空格
        clean = isbn.replace("-", "").replace(" ", "")

        # ISBN-13: 13位数字，以978或979开头
        if len(clean) == 13 and clean.isdigit():
            if clean.startswith("978") or clean.startswith("979"):
                return True

        # ISBN-10: 10位，最后一位可以是X
        if len(clean) == 10:
            if clean[:9].isdigit() and (clean[9].isdigit() or clean[9].upper() == 'X'):
                return True

        raise ISBNFormatError(
            f"ISBN '{isbn}' 格式不正确。\n"
            f"  正确格式示例: 978-7-111-11111-1 或 9787111111111"
        )

    # ---------- 图书管理 ----------

    @log_operation
    def add_book(self, isbn, title, author, publisher, category, stock):
        """
        添加图书

        Args:
            isbn: 国际标准书号
            title: 书名
            author: 作者
            publisher: 出版社
            category: 分类
            stock: 库存数量

        Raises:
            ISBNFormatError: ISBN格式错误
            BookAlreadyExistsError: 图书已存在
            ValueError: 库存数量不合法
        """
        # 验证ISBN
        self.validate_isbn(isbn)

        # 标准化ISBN（移除连字符）
        clean_isbn = isbn.replace("-", "").replace(" ", "")

        # 检查是否已存在
        if clean_isbn in self.books:
            raise BookAlreadyExistsError(f"图书 ISBN {isbn} 已存在")

        # 验证库存
        if not isinstance(stock, int) or stock < 0:
            raise ValueError("库存数量必须是非负整数")

        # 创建图书
        book = Book(clean_isbn, title, author, publisher, category, stock)
        self.books[clean_isbn] = book
        self._save_data()
        return True

    @log_operation
    def remove_book(self, isbn):
        """
        删除图书

        Args:
            isbn: 图书ISBN

        Raises:
            BookNotFoundError: 图书不存在
            LibraryException: 图书还有借出未还
        """
        clean_isbn = isbn.replace("-", "").replace(" ", "")

        if clean_isbn not in self.books:
            raise BookNotFoundError(f"图书 ISBN {isbn} 不存在")

        book = self.books[clean_isbn]
        if book.borrowed > 0:
            raise LibraryException(f"图书《{book.title}》还有 {book.borrowed} 本未归还，无法删除")

        del self.books[clean_isbn]
        self._save_data()
        return True

    @log_operation
    def update_book(self, isbn, **kwargs):
        """
        更新图书信息

        Args:
            isbn: 图书ISBN
            **kwargs: 要更新的字段（title, author, publisher, category, stock）
        """
        clean_isbn = isbn.replace("-", "").replace(" ", "")

        if clean_isbn not in self.books:
            raise BookNotFoundError(f"图书 ISBN {isbn} 不存在")

        book = self.books[clean_isbn]
        allowed_fields = ["title", "author", "publisher", "category"]

        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(book, key, value)
            elif key == "stock":
                if value < book.borrowed:
                    raise LibraryException(f"库存不能小于已借出数量({book.borrowed})")
                book.stock = value

        self._save_data()
        return True

    def get_book(self, isbn):
        """根据ISBN获取图书"""
        clean_isbn = isbn.replace("-", "").replace(" ", "")
        if clean_isbn not in self.books:
            raise BookNotFoundError(f"图书 ISBN {isbn} 不存在")
        return self.books[clean_isbn]

    def search_books(self, keyword, search_by="title"):
        """
        搜索图书

        Args:
            keyword: 搜索关键词
            search_by: 搜索字段（title/author/isbn/category）

        Returns:
            list: 匹配的图书列表
        """
        results = []
        keyword_lower = keyword.lower()

        for book in self.books.values():
            if search_by == "title" and keyword_lower in book.title.lower():
                results.append(book)
            elif search_by == "author" and keyword_lower in book.author.lower():
                results.append(book)
            elif search_by == "isbn" and keyword in book.isbn:
                results.append(book)
            elif search_by == "category" and keyword_lower in book.category.lower():
                results.append(book)

        return results

    def list_books(self, page=1, page_size=10):
        """
        分页显示图书列表

        Args:
            page: 页码（从1开始）
            page_size: 每页数量

        Returns:
            tuple: (当前页图书列表, 总页数)
        """
        all_books = list(self.books.values())
        total = len(all_books)
        total_pages = (total + page_size - 1) // page_size

        start = (page - 1) * page_size
        end = start + page_size

        return all_books[start:end], total_pages

    # ---------- 用户管理 ----------

    @log_operation
    def register_user(self, user_id, name):
        """
        注册用户

        Args:
            user_id: 用户唯一标识
            name: 用户姓名

        Raises:
            UserAlreadyExistsError: 用户已存在
            ValueError: 用户ID或姓名为空
        """
        if not user_id or not name:
            raise ValueError("用户ID和姓名不能为空")

        if user_id in self.users:
            raise UserAlreadyExistsError(f"用户ID {user_id} 已存在")

        user = User(user_id, name)
        self.users[user_id] = user
        self._save_data()
        return True

    @log_operation
    def remove_user(self, user_id):
        """
        删除用户

        Args:
            user_id: 用户ID

        Raises:
            UserNotFoundError: 用户不存在
            LibraryException: 用户还有未还图书
        """
        if user_id not in self.users:
            raise UserNotFoundError(f"用户 {user_id} 不存在")

        user = self.users[user_id]
        if user.borrowed_books:
            raise LibraryException(f"用户 {user.name} 还有 {len(user.borrowed_books)} 本未归还图书，无法删除")

        del self.users[user_id]
        self._save_data()
        return True

    def get_user(self, user_id):
        """根据ID获取用户"""
        if user_id not in self.users:
            raise UserNotFoundError(f"用户 {user_id} 不存在")
        return self.users[user_id]

    def search_users(self, keyword):
        """搜索用户"""
        results = []
        keyword_lower = keyword.lower()
        for user in self.users.values():
            if keyword_lower in user.name.lower() or keyword in user.user_id:
                results.append(user)
        return results

    # ---------- 借阅系统 ----------

    @log_operation
    def borrow_book(self, user_id, isbn):
        """
        借书

        Args:
            user_id: 用户ID
            isbn: 图书ISBN

        Raises:
            UserNotFoundError: 用户不存在
            BookNotFoundError: 图书不存在
            InsufficientStockError: 库存不足
            BorrowLimitExceededError: 超出借阅上限
            BookAlreadyExistsError: 已借阅该图书
        """
        # 检查用户
        if user_id not in self.users:
            raise UserNotFoundError(f"用户 {user_id} 不存在")

        user = self.users[user_id]

        # 检查借阅上限
        if not user.can_borrow:
            raise BorrowLimitExceededError(
                f"用户 {user.name} 已达到最大借阅数量({User.MAX_BORROW}本)"
            )

        # 检查图书
        clean_isbn = isbn.replace("-", "").replace(" ", "")
        if clean_isbn not in self.books:
            raise BookNotFoundError(f"图书 ISBN {isbn} 不存在")

        book = self.books[clean_isbn]

        # 检查库存
        if book.available <= 0:
            raise InsufficientStockError(f"图书《{book.title}》库存不足")

        # 检查是否已借阅
        if clean_isbn in user.borrowed_books:
            raise LibraryException(f"您已借阅《{book.title}》，不能重复借阅")

        # 执行借阅
        book.borrowed += 1
        user.borrowed_books.append(clean_isbn)

        # 创建借阅记录
        record = BorrowRecord(user_id, clean_isbn)
        self.records.append(record)
        user.borrow_history.append(record.record_id)

        self._save_data()
        return record

    @log_operation
    def return_book(self, user_id, isbn):
        """
        还书

        Args:
            user_id: 用户ID
            isbn: 图书ISBN

        Raises:
            UserNotFoundError: 用户不存在
            BookNotFoundError: 图书不存在
            BookNotBorrowedError: 用户未借阅该图书
        """
        # 检查用户
        if user_id not in self.users:
            raise UserNotFoundError(f"用户 {user_id} 不存在")

        user = self.users[user_id]

        # 检查图书
        clean_isbn = isbn.replace("-", "").replace(" ", "")
        if clean_isbn not in self.books:
            raise BookNotFoundError(f"图书 ISBN {isbn} 不存在")

        book = self.books[clean_isbn]

        # 检查用户是否借阅了该图书
        if clean_isbn not in user.borrowed_books:
            raise BookNotBorrowedError(f"用户 {user.name} 未借阅《{book.title}》")

        # 执行归还
        book.borrowed -= 1
        user.borrowed_books.remove(clean_isbn)

        # 更新借阅记录
        for record in self.records:
            if (record.user_id == user_id and 
                record.isbn == clean_isbn and 
                record.status == "借阅中"):
                record.return_book()
                break

        self._save_data()
        return True

    def get_user_records(self, user_id):
        """获取用户的所有借阅记录"""
        if user_id not in self.users:
            raise UserNotFoundError(f"用户 {user_id} 不存在")

        return [r for r in self.records if r.user_id == user_id]

    def get_book_records(self, isbn):
        """获取图书的所有借阅记录"""
        clean_isbn = isbn.replace("-", "").replace(" ", "")
        return [r for r in self.records if r.isbn == clean_isbn]

    # ---------- 数据统计 ----------

    def get_category_stats(self):
        """
        按分类统计图书

        Returns:
            dict: {分类: {"total": 总库存, "available": 可用库存, "borrowed": 已借出}}
        """
        stats = defaultdict(lambda: {"total": 0, "available": 0, "borrowed": 0})

        for book in self.books.values():
            stats[book.category]["total"] += book.stock
            stats[book.category]["available"] += book.available
            stats[book.category]["borrowed"] += book.borrowed

        return dict(stats)

    def get_popular_books(self, top_n=10):
        """
        获取热门借阅图书排行

        Args:
            top_n: 前N名

        Returns:
            list: [(Book, 借阅次数), ...]
        """
        borrow_counts = Counter()
        for record in self.records:
            borrow_counts[record.isbn] += 1

        results = []
        for isbn, count in borrow_counts.most_common(top_n):
            if isbn in self.books:
                results.append((self.books[isbn], count))

        return results

    def get_overdue_records(self):
        """
        获取所有逾期未还的记录

        Returns:
            list: 逾期的 BorrowRecord 列表
        """
        return [r for r in self.records if r.is_overdue]

    def get_overdue_users(self):
        """
        获取逾期未还的用户信息

        Returns:
            dict: {user_id: {"user": User, "overdue_books": [(Book, 逾期天数), ...]}}
        """
        overdue = self.get_overdue_records()
        user_overdue = defaultdict(list)

        for record in overdue:
            if record.isbn in self.books:
                user_overdue[record.user_id].append(
                    (self.books[record.isbn], record.overdue_days)
                )

        result = {}
        for user_id, books in user_overdue.items():
            if user_id in self.users:
                result[user_id] = {
                    "user": self.users[user_id],
                    "overdue_books": books
                }

        return result

    # ---------- 数据导出 ----------

    def export_records_to_csv(self, filename="borrow_records.csv"):
        """导出借阅记录到CSV"""
        with open(filename, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["记录ID", "用户ID", "用户姓名", "ISBN", "书名", 
                            "借阅日期", "应还日期", "归还日期", "状态"])

            for record in self.records:
                book_title = self.books.get(record.isbn, Book("", "未知", "", "", "", 0)).title
                user_name = self.users.get(record.user_id, User("", "未知")).name
                writer.writerow([
                    record.record_id,
                    record.user_id,
                    user_name,
                    record.isbn,
                    book_title,
                    record.borrow_date,
                    record.due_date,
                    record.return_date or "未归还",
                    record.status
                ])

        print(f"  📊 已导出 {len(self.records)} 条记录到 {filename}")
        return True


# ============================================================
# 六、命令行界面（CLI）
# ============================================================

class LibraryCLI:
    """
    命令行交互界面
    提供用户友好的菜单和操作提示
    """

    def __init__(self):
        self.service = LibraryService()
        self.running = True

    def clear_screen(self):
        """清屏"""
        os.system("cls" if os.name == "nt" else "clear")

    def print_header(self, title):
        """打印标题"""
        print("\n" + "=" * 50)
        print(f"  {title}")
        print("=" * 50)

    def print_separator(self):
        """打印分隔线"""
        print("-" * 50)

    def pause(self):
        """暂停等待用户按键"""
        input("\n  按 Enter 键继续...")

    def get_input(self, prompt, allow_empty=False):
        """获取用户输入"""
        while True:
            value = input(f"  {prompt}: ").strip()
            if value or allow_empty:
                return value
            print("  ⚠️ 输入不能为空，请重新输入")

    def get_int_input(self, prompt, min_val=None, max_val=None):
        """获取整数输入"""
        while True:
            try:
                value = int(input(f"  {prompt}: ").strip())
                if min_val is not None and value < min_val:
                    print(f"  ⚠️ 输入不能小于 {min_val}")
                    continue
                if max_val is not None and value > max_val:
                    print(f"  ⚠️ 输入不能大于 {max_val}")
                    continue
                return value
            except ValueError:
                print("  ⚠️ 请输入有效的整数")

    # ---------- 主菜单 ----------

    def run(self):
        """主循环"""
        while self.running:
            self.clear_screen()
            self.print_header("📚 图书管理系统")
            print("""
  【图书管理】
    1. 添加图书
    2. 删除图书
    3. 修改图书信息
    4. 查询图书
    5. 浏览全部图书

  【用户管理】
    6. 注册用户
    7. 删除用户
    8. 查询用户

  【借阅系统】
    9. 借书
   10. 还书
   11. 查看借阅记录

  【数据统计】
   12. 分类统计
   13. 热门图书排行
   14. 逾期未还用户

  【数据管理】
   15. 导出借阅记录(CSV)

   0. 退出系统
            """)

            choice = self.get_input("请选择功能")

            try:
                if choice == "1":
                    self.add_book()
                elif choice == "2":
                    self.remove_book()
                elif choice == "3":
                    self.update_book()
                elif choice == "4":
                    self.search_book()
                elif choice == "5":
                    self.list_books()
                elif choice == "6":
                    self.register_user()
                elif choice == "7":
                    self.remove_user()
                elif choice == "8":
                    self.search_user()
                elif choice == "9":
                    self.borrow_book()
                elif choice == "10":
                    self.return_book()
                elif choice == "11":
                    self.view_records()
                elif choice == "12":
                    self.category_stats()
                elif choice == "13":
                    self.popular_books()
                elif choice == "14":
                    self.overdue_users()
                elif choice == "15":
                    self.export_csv()
                elif choice == "0":
                    self.exit_system()
                else:
                    print("  ⚠️ 无效的选择")
                    self.pause()
            except LibraryException as e:
                print(f"\n  ❌ 操作失败: {e}")
                self.pause()
            except Exception as e:
                print(f"\n  💥 系统错误: {e}")
                self.pause()

    # ---------- 图书管理功能 ----------

    def add_book(self):
        """添加图书"""
        self.print_header("添加图书")

        isbn = self.get_input("请输入ISBN")
        title = self.get_input("请输入书名")
        author = self.get_input("请输入作者")
        publisher = self.get_input("请输入出版社")
        category = self.get_input("请输入分类")
        stock = self.get_int_input("请输入库存数量", min_val=0)

        self.service.add_book(isbn, title, author, publisher, category, stock)
        print(f"\n  ✅ 图书《{title}》添加成功！")
        self.pause()

    def remove_book(self):
        """删除图书"""
        self.print_header("删除图书")

        isbn = self.get_input("请输入要删除的图书ISBN")

        try:
            book = self.service.get_book(isbn)
            confirm = input(f"  确认删除《{book.title}》？(y/n): ").strip().lower()
            if confirm == "y":
                self.service.remove_book(isbn)
                print(f"\n  ✅ 图书《{book.title}》已删除")
            else:
                print("  ℹ️ 已取消删除")
        except BookNotFoundError:
            raise

        self.pause()

    def update_book(self):
        """修改图书信息"""
        self.print_header("修改图书信息")

        isbn = self.get_input("请输入要修改的图书ISBN")
        book = self.service.get_book(isbn)

        print(f"\n  当前信息: {book}")
        print("  直接按Enter跳过不修改的项\n")

        updates = {}

        title = input("  新书名: ").strip()
        if title:
            updates["title"] = title

        author = input("  新作者: ").strip()
        if author:
            updates["author"] = author

        publisher = input("  新出版社: ").strip()
        if publisher:
            updates["publisher"] = publisher

        category = input("  新分类: ").strip()
        if category:
            updates["category"] = category

        stock_input = input("  新库存数量: ").strip()
        if stock_input:
            updates["stock"] = int(stock_input)

        if updates:
            self.service.update_book(isbn, **updates)
            print("\n  ✅ 图书信息已更新")
        else:
            print("\n  ℹ️ 未做任何修改")

        self.pause()

    def search_book(self):
        """查询图书"""
        self.print_header("查询图书")

        print("  搜索方式: 1.书名  2.作者  3.ISBN  4.分类")
        search_type = self.get_input("请选择", allow_empty=True) or "1"

        keyword = self.get_input("请输入搜索关键词")

        search_map = {
            "1": "title",
            "2": "author",
            "3": "isbn",
            "4": "category"
        }
        search_by = search_map.get(search_type, "title")

        results = self.service.search_books(keyword, search_by)

        if results:
            print(f"\n  找到 {len(results)} 本图书:\n")
            for i, book in enumerate(results, 1):
                print(f"  {i}. {book}")
        else:
            print("\n  ℹ️ 未找到匹配的图书")

        self.pause()

    def list_books(self):
        """浏览全部图书"""
        self.print_header("全部图书列表")

        if not self.service.books:
            print("  ℹ️ 图书库为空")
            self.pause()
            return

        page = 1
        page_size = 5

        while True:
            books, total_pages = self.service.list_books(page, page_size)

            print(f"\n  第 {page}/{total_pages} 页 (共 {len(self.service.books)} 本)\n")

            for i, book in enumerate(books, 1):
                status = "🔴 无库存" if book.available == 0 else f"🟢 可借 {book.available} 本"
                print(f"  {(page-1)*page_size + i}. {book} [{status}]")

            print(f"\n  n.下一页  p.上一页  q.返回")
            choice = input("  请选择: ").strip().lower()

            if choice == "n" and page < total_pages:
                page += 1
            elif choice == "p" and page > 1:
                page -= 1
            elif choice == "q":
                break

    # ---------- 用户管理功能 ----------

    def register_user(self):
        """注册用户"""
        self.print_header("注册用户")

        user_id = self.get_input("请输入用户ID")
        name = self.get_input("请输入用户姓名")

        self.service.register_user(user_id, name)
        print(f"\n  ✅ 用户 {name}({user_id}) 注册成功！")
        self.pause()

    def remove_user(self):
        """删除用户"""
        self.print_header("删除用户")

        user_id = self.get_input("请输入要删除的用户ID")

        try:
            user = self.service.get_user(user_id)
            confirm = input(f"  确认删除用户 {user.name}？(y/n): ").strip().lower()
            if confirm == "y":
                self.service.remove_user(user_id)
                print(f"\n  ✅ 用户 {user.name} 已删除")
            else:
                print("  ℹ️ 已取消删除")
        except UserNotFoundError:
            raise

        self.pause()

    def search_user(self):
        """查询用户"""
        self.print_header("查询用户")

        keyword = self.get_input("请输入用户ID或姓名")

        results = self.service.search_users(keyword)

        if results:
            print(f"\n  找到 {len(results)} 个用户:\n")
            for user in results:
                print(f"  • {user}")
                if user.borrowed_books:
                    print(f"    当前借阅: {', '.join(user.borrowed_books)}")
        else:
            print("\n  ℹ️ 未找到匹配的用户")

        self.pause()

    # ---------- 借阅系统功能 ----------

    def borrow_book(self):
        """借书"""
        self.print_header("借书")

        user_id = self.get_input("请输入用户ID")
        user = self.service.get_user(user_id)

        print(f"\n  用户: {user}")

        isbn = self.get_input("请输入图书ISBN")
        book = self.service.get_book(isbn)

        print(f"\n  图书: {book}")

        if book.available <= 0:
            print("  ⚠️ 该图书暂无库存")
            self.pause()
            return

        confirm = input("  确认借阅？(y/n): ").strip().lower()
        if confirm == "y":
            record = self.service.borrow_book(user_id, isbn)
            print(f"\n  ✅ 借阅成功！")
            print(f"  📅 借阅日期: {record.borrow_date}")
            print(f"  📅 应还日期: {record.due_date}")
        else:
            print("  ℹ️ 已取消借阅")

        self.pause()

    def return_book(self):
        """还书"""
        self.print_header("还书")

        user_id = self.get_input("请输入用户ID")
        user = self.service.get_user(user_id)

        print(f"\n  用户: {user}")

        if not user.borrowed_books:
            print("  ℹ️ 该用户当前没有借阅图书")
            self.pause()
            return

        print("  当前借阅图书:")
        for i, isbn in enumerate(user.borrowed_books, 1):
            book = self.service.books.get(isbn)
            if book:
                print(f"    {i}. 《{book.title}》({isbn})")

        isbn = self.get_input("请输入要归还的图书ISBN")
        book = self.service.get_book(isbn)

        confirm = input(f"  确认归还《{book.title}》？(y/n): ").strip().lower()
        if confirm == "y":
            self.service.return_book(user_id, isbn)
            print(f"\n  ✅ 《{book.title}》归还成功！")
        else:
            print("  ℹ️ 已取消归还")

        self.pause()

    def view_records(self):
        """查看借阅记录"""
        self.print_header("借阅记录查询")

        print("  查询方式: 1.按用户  2.按图书  3.全部记录")
        choice = self.get_input("请选择", allow_empty=True) or "1"

        if choice == "1":
            user_id = self.get_input("请输入用户ID")
            records = self.service.get_user_records(user_id)
            user = self.service.get_user(user_id)
            print(f"\n  用户 {user.name} 的借阅记录:\n")
        elif choice == "2":
            isbn = self.get_input("请输入图书ISBN")
            records = self.service.get_book_records(isbn)
            book = self.service.get_book(isbn)
            print(f"\n  图书《{book.title}》的借阅记录:\n")
        else:
            records = self.service.records
            print("\n  全部借阅记录:\n")

        if records:
            for record in records:
                print(f"  • {record}")
        else:
            print("  ℹ️ 暂无记录")

        self.pause()

    # ---------- 数据统计功能 ----------

    def category_stats(self):
        """分类统计"""
        self.print_header("图书分类统计")

        stats = self.service.get_category_stats()

        if not stats:
            print("  ℹ️ 暂无图书数据")
            self.pause()
            return

        print(f"\n  {'分类':<12} {'总库存':>8} {'可借':>8} {'已借出':>8}")
        self.print_separator()

        total_stock = 0
        total_available = 0
        total_borrowed = 0

        for category, data in sorted(stats.items()):
            print(f"  {category:<12} {data['total']:>8} {data['available']:>8} {data['borrowed']:>8}")
            total_stock += data['total']
            total_available += data['available']
            total_borrowed += data['borrowed']

        self.print_separator()
        print(f"  {'合计':<12} {total_stock:>8} {total_available:>8} {total_borrowed:>8}")

        self.pause()

    def popular_books(self):
        """热门图书排行"""
        self.print_header("热门借阅排行")

        top_n = self.get_int_input("显示前N名", min_val=1, max_val=50)

        results = self.service.get_popular_books(top_n)

        if results:
            print(f"\n  {'排名':<6} {'书名':<30} {'借阅次数':>8}")
            self.print_separator()
            for i, (book, count) in enumerate(results, 1):
                print(f"  {i:<6} {book.title:<30} {count:>8}")
        else:
            print("  ℹ️ 暂无借阅记录")

        self.pause()

    def overdue_users(self):
        """逾期未还用户"""
        self.print_header("逾期未还用户")

        overdue = self.service.get_overdue_users()

        if not overdue:
            print("  ✅ 没有逾期未还的用户")
            self.pause()
            return

        print(f"\n  ⚠️ 发现 {len(overdue)} 个用户有逾期未还图书:\n")

        for user_id, data in overdue.items():
            user = data["user"]
            print(f"  用户: {user.name}({user_id})")
            for book, days in data["overdue_books"]:
                print(f"    🔴 《{book.title}》已逾期 {days} 天")
            print()

        self.pause()

    # ---------- 数据导出 ----------

    def export_csv(self):
        """导出CSV"""
        self.print_header("导出借阅记录")

        filename = input("  文件名(默认: borrow_records.csv): ").strip()
        if not filename:
            filename = "borrow_records.csv"
        if not filename.endswith(".csv"):
            filename += ".csv"

        self.service.export_records_to_csv(filename)
        self.pause()

    # ---------- 退出 ----------

    def exit_system(self):
        """退出系统"""
        self.print_header("退出系统")
        confirm = input("  确认退出？(y/n): ").strip().lower()
        if confirm == "y":
            print("\n  👋 感谢使用图书管理系统，再见！")
            self.running = False
        else:
            print("  ℹ️ 已取消退出")
            self.pause()


# ============================================================
# 七、初始化演示数据
# ============================================================

def init_demo_data(service):
    """
    初始化演示数据
    如果数据库为空，自动添加一些示例数据
    """
    if service.books or service.users:
        return  # 已有数据，不覆盖

    print("\n  🎉 首次运行，正在初始化演示数据...\n")

    # 添加图书
    demo_books = [
        ("978-7-111-11111-1", "Python编程：从入门到实践", "Eric Matthes", "人民邮电出版社", "编程", 10),
        ("978-7-111-22222-2", "深入理解计算机系统", "Randal E. Bryant", "机械工业出版社", "计算机", 5),
        ("978-7-111-33333-3", "算法导论", "Thomas H. Cormen", "机械工业出版社", "计算机", 3),
        ("978-7-111-44444-4", "三体", "刘慈欣", "重庆出版社", "科幻", 8),
        ("978-7-111-55555-5", "活着", "余华", "作家出版社", "文学", 6),
        ("978-7-111-66666-6", "百年孤独", "加西亚·马尔克斯", "南海出版公司", "文学", 4),
        ("978-7-111-77777-7", "Java核心技术", "Cay S. Horstmann", "机械工业出版社", "编程", 7),
        ("978-7-111-88888-8", "数据结构与算法分析", "Mark Allen Weiss", "机械工业出版社", "计算机", 5),
    ]

    for book_data in demo_books:
        try:
            service.add_book(*book_data)
        except Exception:
            pass

    # 注册用户
    demo_users = [
        ("U001", "张三"),
        ("U002", "李四"),
        ("U003", "王五"),
    ]

    for user_data in demo_users:
        try:
            service.register_user(*user_data)
        except Exception:
            pass

    # 模拟一些借阅记录
    import random
    borrow_pairs = [
        ("U001", "978-7-111-11111-1"),  # 张三借Python
        ("U001", "978-7-111-44444-4"),  # 张三借三体
        ("U002", "978-7-111-11111-1"),  # 李四借Python
        ("U002", "978-7-111-55555-5"),  # 李四借活着
        ("U003", "978-7-111-11111-1"),  # 王五借Python
        ("U003", "978-7-111-44444-4"),  # 王五借三体
        ("U003", "978-7-111-55555-5"),  # 王五借活着
    ]

    for user_id, isbn in borrow_pairs:
        try:
            service.borrow_book(user_id, isbn)
        except Exception:
            pass

    # 模拟一些归还
    try:
        service.return_book("U002", "978-7-111-55555-5")  # 李四归还活着
    except Exception:
        pass

    # 模拟一个逾期（修改记录日期）
    for record in service.records:
        if record.user_id == "U003" and record.isbn == "978-7-111-44444-4" and record.status == "借阅中":
            # 将借阅日期设为60天前，制造逾期
            old_date = datetime.strptime(record.borrow_date, "%Y-%m-%d")
            new_date = old_date - timedelta(days=60)
            record.borrow_date = new_date.strftime("%Y-%m-%d")
            record.due_date = (new_date + timedelta(days=30)).strftime("%Y-%m-%d")

    service._save_data()
    print("  ✅ 演示数据初始化完成！\n")


# ============================================================
# 八、程序入口
# ============================================================

if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════╗
    ║                                          ║
    ║      📚  图 书 管 理 系 统  v1.0         ║
    ║                                          ║
    ║   支持: 图书管理 | 用户管理 | 借阅系统   ║
    ║         数据统计 | 数据导出 | 日志记录   ║
    ║                                          ║
    ╚══════════════════════════════════════════╝
    """)

    # 创建服务并初始化演示数据
    service = LibraryService()
    init_demo_data(service)

    # 启动命令行界面
    cli = LibraryCLI()
    cli.service = service
    cli.run()
