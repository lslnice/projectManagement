from fastapi import APIRouter, Depends
import aiosqlite
import httpx
from app.database import get_db
from app.dependencies import get_current_user
from app.response import success, error

router = APIRouter(tags=["远程控制"])


@router.post("/projects/{project_id}/remote/toggle")
async def toggle_remote_status(
    project_id: int,
    data: dict,
    db: aiosqlite.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """切换项目远程控制状态（开启/关闭）"""
    cursor = await db.execute(
        "SELECT id, name, remote_control_url, remote_status FROM projects WHERE id = ?",
        (project_id,)
    )
    project = await cursor.fetchone()
    if not project:
        return error(404, "项目不存在")

    new_status = data.get("status")
    if new_status is None:
        # 如果没传状态，则取反
        new_status = 0 if project[3] else 1

    await db.execute(
        "UPDATE projects SET remote_status = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (new_status, project_id)
    )
    await db.commit()

    status_text = "开启" if new_status else "关闭"
    return success({
        "project_id": project_id,
        "remote_status": new_status
    }, f"远程控制已{status_text}")


@router.get("/projects/{project_id}/remote/status")
async def get_remote_status(
    project_id: int,
    db: aiosqlite.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """查询项目远程控制状态"""
    cursor = await db.execute(
        "SELECT id, name, remote_control_url, remote_status FROM projects WHERE id = ?",
        (project_id,)
    )
    project = await cursor.fetchone()
    if not project:
        return error(404, "项目不存在")

    result = {
        "project_id": project[0],
        "name": project[1],
        "remote_control_url": project[2],
        "remote_status": project[3],
    }

    # 如果有远程URL，尝试获取远程状态
    if project[2]:
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(project[2])
                result["remote_response"] = resp.json()
        except Exception:
            result["remote_response"] = None
            result["remote_error"] = "无法连接远程服务"

    return success(result)


@router.get("/remote/check/{project_id}")
async def public_remote_check(
    project_id: int,
    db: aiosqlite.Connection = Depends(get_db)
):
    """公开接口：供客户端检查项目远程状态（无需登录）"""
    cursor = await db.execute(
        "SELECT remote_status FROM projects WHERE id = ?",
        (project_id,)
    )
    project = await cursor.fetchone()
    if not project:
        return {"code": 1000, "data": False, "message": "项目不存在"}

    return {
        "code": 1000,
        "data": bool(project[0]),
        "message": "success"
    }
