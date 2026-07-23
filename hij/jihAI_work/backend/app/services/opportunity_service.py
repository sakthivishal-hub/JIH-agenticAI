from datetime import datetime
from typing import Any

from sqlalchemy.orm import Session

from app.models.opportunity import Opportunity
from app.repositories.opportunity_repository import OpportunityRepository


class OpportunityService:

    def __init__(self, db: Session):
        self.repository = OpportunityRepository(db)

    def create(self, opportunity: Opportunity):
        return self.repository.create(opportunity)

    def get_all(self):
        return self.repository.get_all()

    def search(self, keyword: str):
        return self.repository.search(keyword)

    def get(self, opportunity_id: int):
        return self.repository.get_by_id(opportunity_id)

    def get_or_create_from_payload(self, data: dict[str, Any]) -> Opportunity:
        """Upserts a live search/recommendation result (a plain dict as
        returned by search_agent / the recommender) into the opportunities
        table, keyed on apply_link, and returns the persisted row.

        Needed because bookmarks reference an integer opportunity_id in
        the DB, while search results only ever exist as in-memory dicts
        -- without this, nothing a user finds via search/recommendations
        could ever be bookmarked.
        """
        apply_link = (data.get("apply_link") or "").strip()
        if not apply_link:
            raise ValueError("Opportunity is missing an apply_link, cannot be saved.")

        existing = self.repository.get_by_apply_link(apply_link)
        if existing:
            return existing

        skills = data.get("skills") or []
        if isinstance(skills, list):
            skills = ", ".join(str(s) for s in skills)

        deadline_raw = data.get("deadline")
        deadline = None
        if deadline_raw:
            for fmt in ("%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%d-%m-%Y"):
                try:
                    deadline = datetime.strptime(str(deadline_raw)[:19], fmt).date()
                    break
                except ValueError:
                    continue

        opportunity = Opportunity(
            source=data.get("source", "unknown"),
            opportunity_type=data.get("type", "unknown"),
            title=data.get("title", "Untitled opportunity"),
            company=data.get("company") or "Unknown",
            location=data.get("location", ""),
            salary=data.get("salary", ""),
            deadline=deadline,
            apply_link=apply_link,
            description=data.get("description", ""),
            skills=skills,
        )
        return self.repository.create(opportunity)