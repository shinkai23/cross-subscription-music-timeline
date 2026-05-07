from fastapi import FastAPI
from app.routers.health_router import router as health_router
from app.routers.post_router import router as post_router

app = FastAPI(title="Cross-Subscription Music Timeline API")
app.include_router(health_router)
app.include_router(post_router)

