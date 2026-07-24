from typing import Optional

from sqlalchemy.orm import Session

from app.models.recommendation import Recommendation


class RecommendationRepository:
    """
    Handles all database operations for Recommendation.
    """

    def __init__(self, db: Session):
        self.db = db

    # ==========================
    # CREATE
    # ==========================

    def create(self, recommendation: Recommendation) -> Recommendation:
        self.db.add(recommendation)
        self.db.commit()
        self.db.refresh(recommendation)
        return recommendation

    # ==========================
    # READ
    # ==========================

    def get_by_id(self, recommendation_id: int) -> Optional[Recommendation]:
        return (
            self.db.query(Recommendation)
            .filter(Recommendation.id == recommendation_id)
            .first()
        )

    def get_all(self):
        return (
            self.db.query(Recommendation)
            .order_by(Recommendation.created_at.desc())
            .all()
        )

    def get_by_user(self, user_id: int):
        return (
            self.db.query(Recommendation)
            .filter(Recommendation.user_id == user_id)
            .order_by(Recommendation.match_score.desc())
            .all()
        )

    def get_best_matches(self, user_id: int, limit: int = 10):
        return (
            self.db.query(Recommendation)
            .filter(Recommendation.user_id == user_id)
            .order_by(Recommendation.match_score.desc())
            .limit(limit)
            .all()
        )

    # ==========================
    # UPDATE
    # ==========================

    def update(self, recommendation: Recommendation):
        self.db.commit()
        self.db.refresh(recommendation)
        return recommendation

    def update_score(
        self,
        recommendation: Recommendation,
        score: float,
    ):
        recommendation.match_score = score
        return self.update(recommendation)

    # ==========================
    # DELETE
    # ==========================

    def delete(self, recommendation: Recommendation):
        self.db.delete(recommendation)
        self.db.commit()

    def delete_by_user(self, user_id: int):
        (
            self.db.query(Recommendation)
            .filter(Recommendation.user_id == user_id)
            .delete()
        )
        self.db.commit()

    # ==========================
    # COUNT
    # ==========================

    def count(self):
        return self.db.query(Recommendation).count()