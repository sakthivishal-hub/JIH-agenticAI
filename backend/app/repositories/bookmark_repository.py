from typing import Optional

from sqlalchemy.orm import Session

from app.models.bookmark import Bookmark


class BookmarkRepository:
    """
    Handles all database operations for Bookmark.
    """

    def __init__(self, db: Session):
        self.db = db

    # ==========================
    # CREATE
    # ==========================

    def create(self, bookmark: Bookmark) -> Bookmark:
        self.db.add(bookmark)
        self.db.commit()
        self.db.refresh(bookmark)
        return bookmark

    # ==========================
    # READ
    # ==========================

    def get_by_id(self, bookmark_id: int) -> Optional[Bookmark]:
        return (
            self.db.query(Bookmark)
            .filter(Bookmark.id == bookmark_id)
            .first()
        )

    def get_all(self):
        return (
            self.db.query(Bookmark)
            .order_by(Bookmark.created_at.desc())
            .all()
        )

    def get_user_bookmarks(self, user_id: int):
        return (
            self.db.query(Bookmark)
            .filter(Bookmark.user_id == user_id)
            .order_by(Bookmark.created_at.desc())
            .all()
        )

    def bookmark_exists(
        self,
        user_id: int,
        opportunity_id: int,
    ) -> bool:
        return (
            self.db.query(Bookmark)
            .filter(
                Bookmark.user_id == user_id,
                Bookmark.opportunity_id == opportunity_id,
            )
            .first()
            is not None
        )

    # ==========================
    # DELETE
    # ==========================

    def remove_bookmark(
        self,
        user_id: int,
        opportunity_id: int,
    ):
        (
            self.db.query(Bookmark)
            .filter(
                Bookmark.user_id == user_id,
                Bookmark.opportunity_id == opportunity_id,
            )
            .delete()
        )
        self.db.commit()

    def delete(self, bookmark: Bookmark):
        self.db.delete(bookmark)
        self.db.commit()

    # ==========================
    # COUNT
    # ==========================

    def count(self):
        return self.db.query(Bookmark).count()

    def count_user_bookmarks(self, user_id: int):
        return (
            self.db.query(Bookmark)
            .filter(Bookmark.user_id == user_id)
            .count()
        )