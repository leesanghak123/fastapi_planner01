from fastapi import FastAPI
from contextlib import asynccontextmanager # 수명주기 관리자

from .database.db import create_db_and_tables
from .router import user_api, event_api

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield # 위는 시작, 아래는 종료
    pass

app = FastAPI(lifespan=lifespan)
app.include_router(user_api.router)
app.include_router(event_api.router)