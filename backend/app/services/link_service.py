import random
import string
from sqlalchemy.orm import Session
from app.models.link import Link
from fastapi import HTTPException, status

def generate_short_code(length: int = 6) -> str:
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))

def create_unique_short_code(db: Session, custom_slug: str = None) -> str:
    if custom_slug:
        existing = db.query(Link).filter(Link.short_code == custom_slug).first()
        if existing:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Custom slug already in use")
        return custom_slug
    
    while True:
        code = generate_short_code()
        existing = db.query(Link).filter(Link.short_code == code).first()
        if not existing:
            return code
