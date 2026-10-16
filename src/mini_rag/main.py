from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from mini_rag.api.routes.health import router as health_router
from mini_rag.api.routes.data import router as data_router
from mini_rag.core.config import get_settings
from mini_rag.core.database import create_engine, create_session_factory
from mini_rag.core.exceptions import MiniRagError
from mini_rag.llm.factory import LLMProviderFactory


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()

    engine = create_engine(settings)
    app.state.engine = engine
    app.state.session_factory = create_session_factory(engine)

    factory = LLMProviderFactory(settings)

    generation_llm = factory.create(settings.GENERATION_BACKEND)
    generation_llm.set_generation_model(settings.GENERATION_MODEL_ID)
    app.state.generation_llm = generation_llm

    embedding_llm = factory.create(settings.EMBEDDING_BACKEND)
    embedding_llm.set_embedding_model(
        settings.EMBEDDING_MODEL_ID, settings.EMBEDDING_SIZE
    )
    app.state.embedding_llm = embedding_llm

    yield

    await generation_llm.aclose()
    await embedding_llm.aclose()
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.exception_handler(MiniRagError)
async def mini_rag_error_handler(request: Request, exc: MiniRagError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )


app.include_router(health_router)
app.include_router(data_router)