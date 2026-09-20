from fastapi import APIRouter, Depends, HTTPException, status, Response, Request
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models.link import Link, ClickEvent
from app.models.user import User
from app.schemas.link import LinkCreate, LinkResponse
from app.services.auth_service import get_current_user
from app.services.link_service import create_unique_short_code
from app.services.qr_service import generate_qr_code

router = APIRouter()

# Allow authentication via cookie for API calls from the browser
def get_current_user_cookie(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        scheme, _, token_value = token.partition(" ")
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid token scheme")
        from app.services.auth_service import get_current_user as gcu
        return gcu(token=token_value, db=db)
    except Exception:
        raise HTTPException(status_code=401, detail="Not authenticated")

@router.get("/", response_model=List[LinkResponse])
def get_links(request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_cookie)):
    import os
    public_base_url = os.getenv("PUBLIC_BASE_URL")
    if public_base_url:
        if not public_base_url.endswith('/'):
            public_base_url += '/'
        base_url = public_base_url
    else:
        base_url = str(request.base_url)
        
    links = db.query(Link).filter(Link.owner_id == current_user.id).all()
    
    # attach clicks count to response
    result = []
    for link in links:
        clicks_count = db.query(ClickEvent).filter(ClickEvent.link_id == link.id).count()
        link_dict = {
            "id": link.id,
            "destination_url": link.destination_url,
            "short_code": link.short_code,
            "short_url": f"{base_url}r/{link.short_code}",
            "created_at": link.created_at,
            "is_active": link.is_active,
            "clicks_count": clicks_count
        }
        result.append(link_dict)
    
    return result

@router.post("/", response_model=LinkResponse)
def create_link(link: LinkCreate, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_cookie)):
    import os
    public_base_url = os.getenv("PUBLIC_BASE_URL")
    if public_base_url:
        if not public_base_url.endswith('/'):
            public_base_url += '/'
        base_url = public_base_url
    else:
        base_url = str(request.base_url)
        
    short_code = create_unique_short_code(db, link.custom_slug)
    
    new_link = Link(
        owner_id=current_user.id,
        destination_url=str(link.destination_url),
        short_code=short_code
    )
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    
    return {
        "id": new_link.id,
        "destination_url": new_link.destination_url,
        "short_code": new_link.short_code,
        "short_url": f"{base_url}r/{new_link.short_code}",
        "created_at": new_link.created_at,
        "is_active": new_link.is_active,
        "clicks_count": 0
    }

@router.delete("/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_link(link_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_cookie)):
    link = db.query(Link).filter(Link.id == link_id, Link.owner_id == current_user.id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    db.delete(link)
    db.commit()
    return

@router.get("/{link_id}/qr")
def get_qr_code(link_id: int, request: Request, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_cookie)):
    link = db.query(Link).filter(Link.id == link_id, Link.owner_id == current_user.id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    import os
    public_base_url = os.getenv("PUBLIC_BASE_URL")
    if public_base_url:
        if not public_base_url.endswith('/'):
            public_base_url += '/'
        base_url = public_base_url
    else:
        base_url = str(request.base_url)
        
    redirect_url = f"{base_url}r/{link.short_code}"
    
    img_bytes = generate_qr_code(redirect_url)
    return Response(content=img_bytes, media_type="image/png")
