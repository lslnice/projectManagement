from fastapi import APIRouter, Depends, Query
import aiosqlite
from app.database import get_db
from app.dependencies import get_current_user
from app.response import success, error, paginated

router = APIRouter(tags=["汇款管理"])


@router.get("/payments")
async def list_payments(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    project_id: int = Query(0, description="按项目筛选"),
    keyword: str = Query("", description="搜索订单号"),
    db: aiosqlite.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    conditions = []
    params = []

    if project_id:
        conditions.append("p.project_id = ?")
        params.append(project_id)
    if keyword:
        conditions.append("p.order_no LIKE ?")
        params.append(f"%{keyword}%")

    where = "WHERE " + " AND ".join(conditions) if conditions else ""

    cursor = await db.execute(
        f"SELECT COUNT(*) FROM payments p {where}", params
    )
    total = (await cursor.fetchone())[0]

    offset = (page - 1) * page_size
    cursor = await db.execute(
        f"""SELECT p.*, pr.name as project_name, pr.payment_order_no as project_order_no
            FROM payments p
            LEFT JOIN projects pr ON p.project_id = pr.id
            {where}
            ORDER BY p.created_at DESC LIMIT ? OFFSET ?""",
        params + [page_size, offset]
    )
    rows = await cursor.fetchall()
    items = [dict(row) for row in rows]

    return paginated(items, total, page, page_size)


@router.post("/payments")
async def create_payment(
    data: dict,
    db: aiosqlite.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    order_no = data.get("order_no", "").strip()
    amount = data.get("amount")
    phase = data.get("phase", "")
    notes = data.get("notes", "")
    project_id = data.get("project_id")

    if not order_no:
        return error(400, "订单号不能为空")
    if not amount or amount <= 0:
        return error(400, "汇款金额必须大于0")

    # 如果没有指定项目ID，通过订单号自动匹配项目
    if not project_id:
        cursor = await db.execute(
            """SELECT p.id, p.name FROM projects p
               INNER JOIN project_order_nos o ON o.project_id = p.id
               WHERE o.order_no = ?""",
            (order_no,)
        )
        project = await cursor.fetchone()
        if not project:
            return error(404, f"未找到订单号为 {order_no} 的项目，请手动选择项目或先在项目中绑定此订单号")
        project_id = project[0]
    else:
        cursor = await db.execute("SELECT id FROM projects WHERE id = ?", (project_id,))
        project = await cursor.fetchone()
        if not project:
            return error(404, "项目不存在")

    # 创建汇款记录
    await db.execute(
        "INSERT INTO payments (project_id, order_no, amount, phase, notes) VALUES (?, ?, ?, ?, ?)",
        (project_id, order_no, amount, phase, notes)
    )

    # 更新项目已付金额，并判断是否全款完成
    cursor = await db.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE project_id = ?",
        (project_id,)
    )
    total_paid = (await cursor.fetchone())[0]
    cursor = await db.execute("SELECT total_amount FROM projects WHERE id = ?", (project_id,))
    proj = await cursor.fetchone()
    is_completed = 1 if proj and total_paid >= proj[0] > 0 else 0
    await db.execute(
        "UPDATE projects SET paid_amount = ?, is_completed = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (total_paid, is_completed, project_id)
    )

    await db.commit()
    msg = "汇款记录添加成功"
    if is_completed:
        msg = "汇款记录添加成功，项目已全款完成！"
    return success({"project_id": project_id, "paid_amount": total_paid, "is_completed": is_completed}, msg)


@router.post("/payments/batch")
async def batch_create_payments(
    data: dict,
    db: aiosqlite.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """
    批量导入汇款，支持格式：
    订单号    姓名（忽略）    金额（负数取绝对值）
    """
    text = data.get("text", "").strip()
    phase = data.get("phase", "")
    notes = data.get("notes", "")

    if not text:
        return error(400, "内容不能为空")

    results = []
    failed = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) < 2:
            failed.append({"line": line, "reason": "格式错误，至少需要订单号和金额"})
            continue

        order_no = parts[0].strip()
        # 支持两列（订单号 金额）或三列（订单号 姓名 金额）
        try:
            amount = abs(float(parts[-1]))  # 取最后一列作为金额，取绝对值
        except ValueError:
            failed.append({"line": line, "reason": f"金额格式错误: {parts[-1]}"})
            continue

        if amount <= 0:
            failed.append({"line": line, "reason": "金额必须大于0"})
            continue

        # 通过订单号匹配项目（查 project_order_nos 表）
        cursor = await db.execute(
            """SELECT p.id, p.name FROM projects p
               INNER JOIN project_order_nos o ON o.project_id = p.id
               WHERE o.order_no = ?""",
            (order_no,)
        )
        project = await cursor.fetchone()
        if not project:
            failed.append({"line": line, "reason": f"未找到匹配项目（订单号: {order_no}），请先在项目中绑定此订单号"})
            continue

        project_id = project[0]
        project_name = project[1]

        await db.execute(
            "INSERT INTO payments (project_id, order_no, amount, phase, notes) VALUES (?, ?, ?, ?, ?)",
            (project_id, order_no, amount, phase, notes)
        )
        results.append({"order_no": order_no, "project_name": project_name, "amount": amount})

    # 重新计算所有涉及项目的 paid_amount 和完成状态
    cursor = await db.execute("SELECT DISTINCT project_id FROM payments")
    all_pids = [row[0] for row in await cursor.fetchall()]
    for pid in all_pids:
        cursor = await db.execute("SELECT COALESCE(SUM(amount), 0) FROM payments WHERE project_id = ?", (pid,))
        total_paid = (await cursor.fetchone())[0]
        cursor = await db.execute("SELECT total_amount FROM projects WHERE id = ?", (pid,))
        proj = await cursor.fetchone()
        is_completed = 1 if proj and total_paid >= proj[0] > 0 else 0
        await db.execute(
            "UPDATE projects SET paid_amount = ?, is_completed = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
            (total_paid, is_completed, pid)
        )

    await db.commit()

    return success({
        "success_count": len(results),
        "failed_count": len(failed),
        "success": results,
        "failed": failed,
    }, f"导入完成：成功 {len(results)} 条，失败 {len(failed)} 条")


@router.delete("/payments/{payment_id}")
async def delete_payment(
    payment_id: int,
    db: aiosqlite.Connection = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    cursor = await db.execute("SELECT * FROM payments WHERE id = ?", (payment_id,))
    payment = await cursor.fetchone()
    if not payment:
        return error(404, "汇款记录不存在")

    project_id = payment[1]  # project_id
    await db.execute("DELETE FROM payments WHERE id = ?", (payment_id,))

    # 重新计算项目已付金额和完成状态
    cursor = await db.execute(
        "SELECT COALESCE(SUM(amount), 0) FROM payments WHERE project_id = ?",
        (project_id,)
    )
    total_paid = (await cursor.fetchone())[0]
    cursor = await db.execute("SELECT total_amount FROM projects WHERE id = ?", (project_id,))
    proj = await cursor.fetchone()
    is_completed = 1 if proj and total_paid >= proj[0] > 0 else 0
    await db.execute(
        "UPDATE projects SET paid_amount = ?, is_completed = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (total_paid, is_completed, project_id)
    )

    await db.commit()
    return success(message="删除成功")
