from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.database import engine, Base
from app.routes import auth, links, analytics, bio, redirect, pages

# Create database tables
Base.metadata.create_all(bind=engine)

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="Branded Short-Link & Bio-Link Hub")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# API Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(links.router, prefix="/api/links", tags=["Links"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(bio.router, prefix="/api/bio", tags=["Bio Profile"])

# Pages and redirect routes
app.include_router(pages.router, tags=["Pages"])
app.include_router(redirect.router, prefix="/r", tags=["Redirect"])

@app.on_event("startup")
async def startup_event():
    print("Application has started.")
