from sqlalchemy import Column, Integer, ForeignKey, Float, TIMESTAMP, func, UUID, ARRAY
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class PodcastProgress(Base):
    __tablename__ = "podcast_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    podcast_id = Column(UUID(as_uuid=True), ForeignKey("podcasts.id", ondelete="CASCADE"))
    current_position = Column(Integer, default=0)
    playback_speed = Column(Float, default=1.0)
    completed_segments = Column(ARRAY(Integer), default=[])
    completion_percentage = Column(Float, default=0.0)
    last_played_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # # Relationships
    user = relationship("User", back_populates="podcast_progress")
    podcast = relationship("Podcast", back_populates="progress")