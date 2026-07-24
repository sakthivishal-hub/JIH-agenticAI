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