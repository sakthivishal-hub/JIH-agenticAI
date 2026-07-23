from datetime import UTC, datetime
from app.core.database import Base
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Integer,
    String,
    Text,
)

class User(Base):
    __tablename__ = "users"

    # Primary Key
    id = Column(Integer, primary_key=True, index=True)

    # Authentication
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Academic Information
    college = Column(String(255), nullable=True)
    degree = Column(String(150), nullable=True)
    branch = Column(String(150), nullable=True)
    year = Column(Integer, nullable=True)

    # Career Profile
    skills = Column(Text, nullable=True)
    interests = Column(Text, nullable=True)
    preferred_role = Column(String(150), nullable=True)
    preferred_location = Column(String(150), nullable=True)
    current_location = Column(String(150), nullable=True)

    # Parsed resume text (raw dict from resume_parser, stored as text) --
    # consumed by /recommendations as the source resume for AI matching.
    resume_text = Column(Text, nullable=True)

    # Notification Preferences (email / WhatsApp)
    whatsapp_number = Column(String(20), nullable=True)
    notify_email = Column(Boolean, default=True)
    notify_whatsapp = Column(Boolean, default=False)

    # Professional Links
    linkedin_url = Column(String(500), nullable=True)
    github_url = Column(String(500), nullable=True)
    portfolio_url = Column(String(500), nullable=True)

    # Profile
    profile_picture = Column(String(500), nullable=True)
    bio = Column(Text, nullable=True)

    # Account Status
    role = Column(String(50), default="user")
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)

    # Timestamps
    # Timestamps
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
    )

    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    @property
    def has_resume(self) -> bool:
        """Not a DB column -- lets API responses expose whether a resume
        is on file without shipping the full parsed resume_text."""
        return bool(self.resume_text)