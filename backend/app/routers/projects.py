from fastapi import APIRouter, Depends, Query
import aiosqlite
from datetime import datetime, timezone
from app.database import get_db
from app.dependencies import get_current_user
from app.response import success, error, paginated

router = APIRouter(tags=["项目管理"])


async def _attach_order_nos(db, items):
    """为项目列表附加订单号列表"""
    if not items:
        return items
    ids = [item["id"] for item in items]
    placeholders = ",".join("?" * len(ids))
    cursor = await db.execute(
        f"SELECT project_id, order_no FROM project_order_nos WHERE project_id IN ({placeholders})",
        ids
    )
    rows = await cursor.fetchall()
    order_map = {}
    for row in rows:
        order_map.setdefault(row[0], []).append(row[1])
    for item in items:
        item["order_nos"] = order_map.get(item["id"], [])
    return items


async def _sync_order_nos(db, project_id, order_nos: list):
    """同步项目订单号：删旧增新"""
    await db.execute("DELETE FROM project_order_nos WHERE project_id = ?", (project_id,))
    for no in order_nos:
        no = no.strip()
        if no:
            await db.execute(
                "INSERT OR IGNORE INTO project_order_nos (project_id, order_no) VALUES (?, ?)",
                (project_id, no)
            )


@router.get("/projects")
async def list_projects(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: str = Query("", description="搜索关键词"),
    completed: int = Query(0, description="0=进行中, 1=已完成"),
    dev_status: str = Query("", description="开发状态筛选"),
    db: aiosqlite.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    conditions = ["p.is_completed = ?"]
    params = [completed]

    if keyword:
        conditions.append("""(p.name LIKE ? OR EXISTS (
            SELECT 1 FROM project_order_nos o WHERE o.project_id = p.id AND o.order_no LIKE ?
        ))""")
        params.extend([f"%{keyword}%", f"%{keyword}%"])
    if dev_status:
        conditions.append("p.dev_status = ?")
        params.append(dev_status)

    where = "WHERE " + " AND ".join(conditions) if conditions else ""

    cursor = await db.execute(f"SELECT COUNT(*) FROM projects p {where}", params)
    total = (await cursor.fetchone())[0]

    offset = (page - 1) * page_size
    cursor = await db.execute(
        f"SELECT p.* FROM projects p {where} ORDER BY p.created_at DESC LIMIT ? OFFSET ?",
        params + [page_size, offset]
    )
    rows = await cursor.fetchall()
    items = [dict(row) for row in rows]
    items = await _attach_order_nos(db, items)

    return paginated(items, total, page, page_size)


@router.get("/projects/stats/overview")
async def project_stats(
    db: aiosqlite.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = await db.execute("SELECT COUNT(*) FROM projects")
    total = (await cursor.fetchone())[0]

    cursor = await db.execute("SELECT COUNT(*) FROM projects WHERE status = 'active'")
    active = (await cursor.fetchone())[0]

    cursor = await db.execute("SELECT COUNT(*) FROM projects WHERE status = 'completed'")
    completed = (await cursor.fetchone())[0]

    cursor = await db.execute("SELECT COALESCE(SUM(total_amount), 0) FROM projects")
    total_amount = (await cursor.fetchone())[0]

    cursor = await db.execute("SELECT COALESCE(SUM(paid_amount), 0) FROM projects")
    paid_amount = (await cursor.fetchone())[0]

    cursor = await db.execute("SELECT COALESCE(SUM(total_amount * commission_rate), 0) FROM projects")
    total_commission = (await cursor.fetchone())[0]

    cursor = await db.execute("SELECT COALESCE(SUM(paid_amount * commission_rate), 0) FROM projects")
    paid_commission = (await cursor.fetchone())[0]

    return success({
        "total_projects": total,
        "active_projects": active,
        "completed_projects": completed,
        "total_amount": total_amount,
        "paid_amount": paid_amount,
        "unpaid_amount": total_amount - paid_amount,
        "total_commission": round(total_commission, 2),
        "paid_commission": round(paid_commission, 2),
    })


@router.get("/projects/{project_id}")
async def get_project(
    project_id: int,
    db: aiosqlite.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = await db.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = await cursor.fetchone()
    if not project:
        return error(404, "项目不存在")
    item = dict(project)
    items = await _attach_order_nos(db, [item])
    return success(items[0])


@router.post("/projects")
async def create_project(
    data: dict,
    db: aiosqlite.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    name = data.get("name")
    if not name:
        return error(400, "项目名称不能为空")

    total_amount = data.get("total_amount", 0)
    commission_rate = data.get("commission_rate", 0.7)
    dev_status = data.get("dev_status", "developing")
    notes = data.get("notes", "")
    order_nos = data.get("order_nos", [])

    now = datetime.now(timezone.utc).isoformat()
    cursor = await db.execute(
        """INSERT INTO projects (name, total_amount, payment_order_no, commission_rate,
           remote_status, progress, dev_status, is_completed, notes, created_at, updated_at)
           VALUES (?, ?, ?, ?, 1, 0, ?, 0, ?, ?, ?)""",
        (name, total_amount, order_nos[0] if order_nos else "", commission_rate, dev_status, notes, now, now)
    )
    project_id = cursor.lastrowid
    await _sync_order_nos(db, project_id, order_nos)
    await db.commit()
    return success({"id": project_id}, "创建成功")


@router.put("/projects/{project_id}")
async def update_project(
    project_id: int,
    data: dict,
    db: aiosqlite.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = await db.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = await cursor.fetchone()
    if not project:
        return error(404, "项目不存在")

    fields = []
    params = []
    for key in ["name", "total_amount", "commission_rate", "progress", "dev_status", "notes"]:
        if key in data:
            fields.append(f"{key} = ?")
            params.append(data[key])

    # 同步订单号
    if "order_nos" in data:
        order_nos = data["order_nos"]
        await _sync_order_nos(db, project_id, order_nos)
        # 同步更新 payment_order_no 字段（兼容）
        fields.append("payment_order_no = ?")
        params.append(order_nos[0] if order_nos else "")

    if fields:
        fields.append("updated_at = ?")
        params.append(datetime.now(timezone.utc).isoformat())
        params.append(project_id)
        await db.execute(f"UPDATE projects SET {', '.join(fields)} WHERE id = ?", params)

    await db.commit()
    return success(message="更新成功")


@router.delete("/projects/{project_id}")
async def delete_project(
    project_id: int,
    db: aiosqlite.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = await db.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
    project = await cursor.fetchone()
    if not project:
        return error(404, "项目不存在")

    await db.execute("DELETE FROM payments WHERE project_id = ?", (project_id,))
    await db.execute("DELETE FROM project_order_nos WHERE project_id = ?", (project_id,))
    await db.execute("DELETE FROM projects WHERE id = ?", (project_id,))
    await db.commit()
    return success(message="删除成功")
