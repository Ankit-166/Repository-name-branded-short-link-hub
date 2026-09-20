from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.bio import BioProfile, BioLink
from app.models.user import User
from app.schemas.bio import BioProfileCreate, BioProfileResponse, BioLinkCreate, BioLinkResponse
from app.routes.links import get_current_user_cookie
from typing import List

router = APIRouter()

@router.get("/me", response_model=BioProfileResponse)
def get_my_bio(db: Session = Depends(get_db), current_user: User = Depends(get_current_user_cookie)):
    profile = db.query(BioProfile).filter(BioProfile.owner_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Bio profile not found")
    return profile

@router.put("/me", response_model=BioProfileResponse)
def update_my_bio(bio_data: BioProfileCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_cookie)):
    profile = db.query(BioProfile).filter(BioProfile.owner_id == current_user.id).first()
    
    if not profile:
        # Create new profile
        profile = BioProfile(
            owner_id=current_user.id,
            username=current_user.username,
            display_name=bio_data.display_name or current_user.name,
            bio=bio_data.bio,
            theme=bio_data.theme
        )
        db.add(profile)
    else:
        profile.display_name = bio_data.display_name
        profile.bio = bio_data.bio
        profile.theme = bio_data.theme
        
    db.commit()
    db.refresh(profile)
    return profile

@router.post("/links", response_model=BioLinkResponse)
def add_bio_link(link_data: BioLinkCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_cookie)):
    profile = db.query(BioProfile).filter(BioProfile.owner_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Create a bio profile first")
    
    new_link = BioLink(
        bio_profile_id=profile.id,
        title=link_data.title,
        url=str(link_data.url),
        platform=link_data.platform
    )
    db.add(new_link)
    db.commit()
    db.refresh(new_link)
    return new_link

@router.delete("/links/{link_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_bio_link(link_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user_cookie)):
    profile = db.query(BioProfile).filter(BioProfile.owner_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Bio profile not found")
        
    link = db.query(BioLink).filter(BioLink.id == link_id, BioLink.bio_profile_id == profile.id).first()
    if not link:
        raise HTTPException(status_code=404, detail="Bio link not found")
        
    db.delete(link)
    db.commit()
    return
