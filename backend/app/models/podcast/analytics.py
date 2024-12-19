from sqlalchemy import Column, Integer, ForeignKey, Float, TIMESTAMP, func, UUID, Date
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class PodcastAnalytics(Base):
    __tablename__ = "podcast_analytics"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))
    podcast_id = Column(UUID(as_uuid=True), ForeignKey("podcasts.id", ondelete="CASCADE"))
    date = Column(Date, nullable=False)
    total_time_listened = Column(Integer, default=0)
    average_speed = Column(Float, default=1.0)
    number_of_sessions = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="podcast_analytics")
    podcast = relationship("Podcast", back_populates="analytics")