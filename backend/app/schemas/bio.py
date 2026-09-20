from pydantic import BaseModel, HttpUrl
from typing import Optional, List

class BioLinkBase(BaseModel):
    title: str
    url: HttpUrl
    platform: Optional[str] = None

class BioLinkCreate(BioLinkBase):
    pass

class BioLinkResponse(BioLinkBase):
    id: int
    display_order: int

    class Config:
        from_attributes = True

class BioProfileBase(BaseModel):
    display_name: Optional[str] = None
    bio: Optional[str] = None
    theme: Optional[str] = "minimal-light"

class BioProfileCreate(BioProfileBase):
    pass

class BioProfileResponse(BioProfileBase):
    id: int
    username: str
    avatar: Optional[str] = None
    links: List[BioLinkResponse] = []

    class Config:
        from_attributes = True
