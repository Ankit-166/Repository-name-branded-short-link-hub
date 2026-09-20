from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database import get_db
from app.models.link import Link, ClickEvent
from app.models.user import User
from app.schemas.link import ClickAnalytics
from app.routes.links import get_current_user_cookie
from collections import defaultdict

router = APIRouter()

@router.get("/{link_id}", response_model=ClickAnalytics)
def get_link_analytics(link_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_cookie)):
    link = db.query(Link).filter(Link.id == link_id, Link.owner_id == current_user.id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    
    clicks = db.query(ClickEvent).filter(ClickEvent.link_id == link_id).all()
    
    total_clicks = len(clicks)
    
    clicks_by_date = defaultdict(int)
    top_referrers = defaultdict(int)
    device_distribution = defaultdict(int)
    
    for click in clicks:
        date_str = click.timestamp.strftime("%Y-%m-%d") if click.timestamp else "Unknown"
        clicks_by_date[date_str] += 1
        
        referrer = click.referrer or "Direct"
        top_referrers[referrer] += 1
        
        device = click.device_type or "Unknown"
        device_distribution[device] += 1
        
    # Sort top referrers
    sorted_referrers = dict(sorted(top_referrers.items(), key=lambda item: item[1], reverse=True)[:5])
    
    return {
        "total_clicks": total_clicks,
        "clicks_by_date": dict(clicks_by_date),
        "top_referrers": sorted_referrers,
        "device_distribution": dict(device_distribution)
    }
