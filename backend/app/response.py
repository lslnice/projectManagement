from fastapi.responses import JSONResponse


def success(data=None, message="ok"):
    return {"code": 200, "data": data, "message": message}


def error(code=400, message="error"):
    return JSONResponse(status_code=code, content={"code": code, "message": message})


def paginated(items, total, page, page_size):
    return success({
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size
    })
