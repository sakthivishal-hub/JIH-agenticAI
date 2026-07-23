from sqlalchemy.orm import Session

from app.models.recommendation import Recommendation
from app.repositories.recommendation_repository import RecommendationRepository


class RecommendationService:

    def __init__(self, db: Session):
        self.repository = RecommendationRepository(db)

    def create(self, recommendation: Recommendation):
        return self.repository.create(recommendation)

    def get_user_recommendations(self, user_id: int):
        return self.repository.get_user_recommendations(user_id)