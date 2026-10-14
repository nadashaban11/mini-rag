from fastapi import APIRouter
from fastapi import APIRouter, Depends
from mini_rag.api.dependencies import get_session
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession


router = APIRouter(
    prefix="/api/v1",
    tags=["health"],
)
    

@router.get("/health")
async def health(session: AsyncSession = Depends(get_session)):
    await session.execute(text("SELECT 1"))
    return {"status": "ok", "database": "ok"}
