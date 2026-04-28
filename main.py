from fastapi import APIRouter, FastAPI

from app.api.v2.operations import router as operations_router
from app.api.v2.users import router as users_router
from app.api.v2.wallets import router as wallets_router
from app.api.v2.predict import router as predict_router
from app.database import Base, engine

app = FastAPI()
router = APIRouter(prefix="/api/v2")

app.include_router(wallets_router, tags=["wallets"])
app.include_router(operations_router, tags=["operations"])
app.include_router(users_router, tags=["users"])
app.include_router(predict_router, tags=["language"])

Base.metadata.create_all(bind=engine)
