from sqlalchemy import Column, String, Integer, ForeignKey, Text, TIMESTAMP, func, UUID
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class Podcast(Base):
    __tablename__ = "podcasts"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    file_id = Column(UUID(as_uuid=True), ForeignKey("files.id", ondelete="CASCADE"))
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    title = Column(String, nullable=False)
    description = Column(Text)
    duration = Column(Integer, nullable=False)  # in seconds
    s3_audio_key = Column(String, nullable=False)
    s3_transcript_txt_key = Column(String, nullable=False)
    s3_transcript_vtt_key = Column(String)
    transcript_status = Column(String, default="txt_only")
    total_plays = Column(Integer, default=0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # # Relationships
    user = relationship("User", back_populates="podcasts")
    file = relationship("File", back_populates="podcasts")
    progress = relationship("PodcastProgress", back_populates="podcast", cascade="all, delete-orphan")
    analytics = relationship("PodcastAnalytics", back_populates="podcast", cascade="all, delete-orphan")