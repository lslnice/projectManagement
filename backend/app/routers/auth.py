from fastapi import APIRouter, Depends
import aiosqlite
from app.database import get_db
from app.auth import verify_password, create_access_token
from app.dependencies import get_current_user
from app.response import success, error

router = APIRouter(tags=["认证"])


@router.post("/login")
async def login(data: dict, db: aiosqlite.Connection = Depends(get_db)):
    username = data.get("username")
    password = data.get("password")
    if not username or not password:
        return error(400, "用户名和密码不能为空")

    cursor = await db.execute("SELECT id, username, password_hash, is_admin FROM users WHERE username = ?", (username,))
    user = await cursor.fetchone()
    if not user or not verify_password(password, user[2]):
        return error(401, "用户名或密码错误")

    token = create_access_token({"sub": str(user[0])})
    return success({"token": token})


@router.get("/me")
async def get_me(current_user: dict = Depends(get_current_user)):
    return success(current_user)
