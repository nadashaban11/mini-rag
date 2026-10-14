from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from mini_rag.api.routes.health import router as health_router
from mini_rag.api.routes.upload import router as upload_router
from mini_rag.core.config import get_settings
from mini_rag.core.database import create_engine, create_session_factory
from mini_rag.core.exceptions import MiniRagError


@asynccontextmanager
async def lifespan(app: FastAPI):
    engine = create_engine(get_settings())
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(MiniRagError)
async def mini_rag_error_handler(request: Request, exc: MiniRagError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


app.include_router(health_router)
app.include_router(upload_router)