import aiosqlite
import os

DB_PATH = os.environ.get(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(os.path.dirname(__file__)), "project_management.db")
)


async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA foreign_keys = ON")
    try:
        yield db
    finally:
        await db.close()


async def init_db():
    db = await aiosqlite.connect(DB_PATH)
    await db.execute("PRAGMA foreign_keys = ON")

    # 用户表
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            is_admin INTEGER DEFAULT 1,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 项目表
    await db.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            total_amount REAL NOT NULL DEFAULT 0,
            paid_amount REAL NOT NULL DEFAULT 0,
            payment_order_no TEXT,
            commission_rate REAL NOT NULL DEFAULT 0.7,
            remote_control_url TEXT,
            remote_status INTEGER DEFAULT 1,
            progress INTEGER DEFAULT 0,
            dev_status TEXT DEFAULT 'developing',
            is_completed INTEGER DEFAULT 0,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            updated_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 迁移旧数据库：添加新字段（已存在则忽略）
    for col, definition in [
        ("dev_status", "TEXT DEFAULT 'developing'"),
        ("is_completed", "INTEGER DEFAULT 0"),
    ]:
        try:
            await db.execute(f"ALTER TABLE projects ADD COLUMN {col} {definition}")
        except Exception:
            pass

    # 项目订单号表（一个项目可绑定多个订单号）
    await db.execute("""
        CREATE TABLE IF NOT EXISTS project_order_nos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            order_no TEXT NOT NULL UNIQUE,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # 汇款记录表
    await db.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            order_no TEXT NOT NULL,
            amount REAL NOT NULL,
            phase TEXT,
            notes TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)

    # 创建默认管理员（首次运行）
    from app.auth import hash_password
    cursor = await db.execute("SELECT COUNT(*) FROM users")
    count = (await cursor.fetchone())[0]
    if count == 0:
        password_hash = hash_password("admin123")
        await db.execute(
            "INSERT INTO users (username, password_hash, is_admin) VALUES (?, ?, ?)",
            ("admin", password_hash, 1)
        )

    await db.commit()
    await db.close()
