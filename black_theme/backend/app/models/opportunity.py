from sqlalchemy import (
    Column,
    DateTime,
    Integer,
    String,
    Text,
)
from sqlalchemy.sql import func

from app.core.database import Base
from sqlalchemy import Date

class Opportunity(Base):
    __tablename__ = "opportunities"

    id = Column(Integer, primary_key=True, index=True)

    source = Column(String(100), nullable=False, index=True)

    opportunity_type = Column(String(50), nullable=False)

    title = Column(String(255), nullable=False, index=True)

    company = Column(String(255), nullable=False)

    location = Column(String(150))

    salary = Column(String(100))

    deadline = Column(Date,nullable=True)

    apply_link = Column(String(500), unique=True, nullable=False)

    description = Column(Text)

    skills = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )