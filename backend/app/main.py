from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="项目管理系统", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

prefix = "/api/v1"

from app.routers import auth, projects, payments, remote_control

app.include_router(auth.router, prefix=prefix)
app.include_router(projects.router, prefix=prefix)
app.include_router(payments.router, prefix=prefix)
app.include_router(remote_control.router, prefix=prefix)
