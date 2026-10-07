from fastapi import FastAPI
from mini_rag.api.routes.health import router as health_router
from mini_rag.api.routes.upload import router as upload_router



app = FastAPI()

app.include_router(health_router)
app.include_router(upload_router)
