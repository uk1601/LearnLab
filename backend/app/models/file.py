from sqlalchemy import Column, String, DateTime, BigInteger, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from ..core.database import Base
from datetime import datetime

class File(Base):
    __tablename__ = "files"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    filename = Column(String)
    s3_key = Column(String)
    file_size = Column(BigInteger)
    mime_type = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_deleted = Column(Boolean, default=False)

    # Relationships
    user = relationship("User", back_populates="files")
    deck = relationship("FlashcardDeck", back_populates="file", uselist=False)  # one-to-one relationship
    podcasts = relationship("Podcast", back_populates="file", uselist=False)  # one-to-one relationship
    quizzes = relationship("Quiz", back_populates="file", cascade="all, delete-orphan")  # one-to-many relationship