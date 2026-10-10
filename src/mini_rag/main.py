from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from mini_rag.api.routes.health import router as health_router
from mini_rag.api.routes.upload import router as upload_router
from mini_rag.core.exceptions import MiniRagError



app = FastAPI()


@app.exception_handler(MiniRagError)
async def mini_rag_error_handler(request: Request, exc: MiniRagError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.message},
    )

app.include_router(health_router)
app.include_router(upload_router)
