from datetime import UTC, datetime

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from app.core.database import Base


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    filename = Column(String(255), nullable=False)
    file_size = Column(Integer)
    file_type = Column(String(20))
    file_path = Column(String(500), nullable=True)

    extracted_text = Column(Text, nullable=True)

    summary = Column(Text, nullable=True)

    skills = Column(Text, nullable=True)

    education = Column(Text, nullable=True)

    experience = Column(Text, nullable=True)

    projects = Column(Text, nullable=True)

    certifications = Column(Text, nullable=True)

    languages = Column(Text, nullable=True)

    resume_score = Column(Integer, default=0)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    user = relationship("User", backref="resumes")