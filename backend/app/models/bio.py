from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

class BioProfile(Base):
    __tablename__ = "bio_profiles"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), unique=True)
    username = Column(String, unique=True, index=True, nullable=False)
    avatar = Column(String)
    display_name = Column(String)
    bio = Column(String)
    theme = Column(String, default="minimal-light")

    links = relationship("BioLink", back_populates="profile", cascade="all, delete-orphan")

class BioLink(Base):
    __tablename__ = "bio_links"

    id = Column(Integer, primary_key=True, index=True)
    bio_profile_id = Column(Integer, ForeignKey("bio_profiles.id"))
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    platform = Column(String) # For optional icons
    display_order = Column(Integer, default=0)

    profile = relationship("BioProfile", back_populates="links")
