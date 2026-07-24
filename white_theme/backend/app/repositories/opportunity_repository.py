from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity


class OpportunityRepository:
    """
    Handles all database operations for Opportunity.
    """

    def __init__(self, db: Session):
        self.db = db

    # ==========================
    # CREATE
    # ==========================

    def create(self, opportunity: Opportunity) -> Opportunity:
        self.db.add(opportunity)
        self.db.commit()
        self.db.refresh(opportunity)
        return opportunity

    # ==========================
    # READ
    # ==========================

    def get_by_id(self, opportunity_id: int) -> Optional[Opportunity]:
        return (
            self.db.query(Opportunity)
            .filter(Opportunity.id == opportunity_id)
            .first()
        )

    def get_all(self):
        return (
            self.db.query(Opportunity)
            .order_by(Opportunity.created_at.desc())
            .all()
        )

    def get_by_apply_link(self, apply_link: str) -> Optional[Opportunity]:
        return (
            self.db.query(Opportunity)
            .filter(Opportunity.apply_link == apply_link)
            .first()
        )

    def get_latest(self, limit: int = 20):
        return (
            self.db.query(Opportunity)
            .order_by(Opportunity.created_at.desc())
            .limit(limit)
            .all()
        )

    # ==========================
    # SEARCH
    # ==========================

    def search(self, keyword: str):
        return (
            self.db.query(Opportunity)
            .filter(
                or_(
                    Opportunity.title.ilike(f"%{keyword}%"),
                    Opportunity.company.ilike(f"%{keyword}%"),
                    Opportunity.skills.ilike(f"%{keyword}%"),
                    Opportunity.description.ilike(f"%{keyword}%"),
                )
            )
            .all()
        )

    def filter_by_company(self, company: str):
        return (
            self.db.query(Opportunity)
            .filter(Opportunity.company.ilike(f"%{company}%"))
            .all()
        )

    def filter_by_location(self, location: str):
        return (
            self.db.query(Opportunity)
            .filter(Opportunity.location.ilike(f"%{location}%"))
            .all()
        )

    def filter_by_type(self, opportunity_type: str):
        return (
            self.db.query(Opportunity)
            .filter(
                Opportunity.opportunity_type == opportunity_type
            )
            .all()
        )

    # ==========================
    # UPDATE
    # ==========================

    def update(self, opportunity: Opportunity):
        self.db.commit()
        self.db.refresh(opportunity)
        return opportunity

    # ==========================
    # DELETE
    # ==========================

    def delete(self, opportunity: Opportunity):
        self.db.delete(opportunity)
        self.db.commit()

    # ==========================
    # COUNT
    # ==========================

    def count(self):
        return self.db.query(Opportunity).count()

    # ==========================
    # PAGINATION
    # ==========================

    def paginate(
        self,
        skip: int = 0,
        limit: int = 20,
    ):
        return (
            self.db.query(Opportunity)
            .offset(skip)
            .limit(limit)
            .all()
        )