from sqlalchemy.orm import Session

from app.models.bookmark import Bookmark
from app.repositories.bookmark_repository import BookmarkRepository


class BookmarkService:

    def __init__(self, db: Session):
        self.repository = BookmarkRepository(db)

    def create(self, bookmark: Bookmark):
        return self.repository.create(bookmark)

    def get_user_bookmarks(self, user_id: int):
        return self.repository.get_user_bookmarks(user_id)

    def delete(self, bookmark: Bookmark):
        self.repository.delete(bookmark)