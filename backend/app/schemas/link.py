from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional, List

class LinkBase(BaseModel):
    destination_url: HttpUrl

class LinkCreate(LinkBase):
    custom_slug: Optional[str] = None

class LinkResponse(LinkBase):
    id: int
    short_code: str
    short_url: Optional[str] = None
    created_at: datetime
    is_active: bool
    clicks_count: int = 0

    class Config:
        from_attributes = True

class ClickAnalytics(BaseModel):
    total_clicks: int
    clicks_by_date: dict
    top_referrers: dict
    device_distribution: dict
