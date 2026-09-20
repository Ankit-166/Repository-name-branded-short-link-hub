from fastapi import APIRouter, Request, Depends, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.bio import BioProfile
import os

router = APIRouter()

# Setup templates directory
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse(request=request, name="index.html")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html")

@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse(request=request, name="signup.html")

@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse(request=request, name="dashboard.html")

@router.get("/bio/{username}", response_class=HTMLResponse)
async def public_bio_page(username: str, request: Request, db: Session = Depends(get_db)):
    profile = db.query(BioProfile).filter(BioProfile.username == username).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Bio not found")
    
    return templates.TemplateResponse(request=request, name="public_bio.html", context={"profile": profile})
