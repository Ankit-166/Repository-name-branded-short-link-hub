from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
import hashlib
from app.database import get_db
from app.models.link import Link, ClickEvent

router = APIRouter()

@router.get("/{short_code}")
def redirect_to_original(short_code: str, request: Request, db: Session = Depends(get_db)):
    link = db.query(Link).filter(Link.short_code == short_code).first()
    
    if not link or not link.is_active:
        raise HTTPException(status_code=404, detail="Link not found or inactive")
    
    # Record click event
    referrer = request.headers.get("referer", "")
    user_agent = request.headers.get("user-agent", "").lower()
    
    device_type = "Desktop"
    if "mobile" in user_agent or "android" in user_agent or "iphone" in user_agent:
        device_type = "Mobile"
    elif "tablet" in user_agent or "ipad" in user_agent:
        device_type = "Tablet"
        
    client_ip = request.client.host if request.client else "unknown"
    ip_hash = hashlib.sha256(client_ip.encode()).hexdigest()
    
    click = ClickEvent(
        link_id=link.id,
        referrer=referrer,
        device_type=device_type,
        ip_hash=ip_hash
    )
    db.add(click)
    db.commit()
    
    return RedirectResponse(url=link.destination_url, status_code=302)
