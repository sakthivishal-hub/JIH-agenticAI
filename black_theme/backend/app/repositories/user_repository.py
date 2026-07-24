from typing import Optional

from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.user import User


class UserRepository:
    """
    Handles all database operations for User.
    """

    def __init__(self, db: Session):
        self.db = db

    # ==========================
    # CREATE
    # ==========================

    def create(self, user: User) -> User:
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    # ==========================
    # READ
    # ==========================

    def get_by_id(self, user_id: int) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.id == user_id)
            .first()
        )

    def get_by_email(self, email: str) -> Optional[User]:
        return (
            self.db.query(User)
            .filter(User.email == email)
            .first()
        )

    def get_by_name(self, name: str):
        return (
            self.db.query(User)
            .filter(User.name.ilike(f"%{name}%"))
            .all()
        )

    def get_all(self):
        return (
            self.db.query(User)
            .order_by(User.id)
            .all()
        )

    # ==========================
    # SEARCH
    # ==========================

    def search(self, keyword: str):
        return (
            self.db.query(User)
            .filter(
                or_(
                    User.name.ilike(f"%{keyword}%"),
                    User.email.ilike(f"%{keyword}%"),
                    User.preferred_role.ilike(f"%{keyword}%"),
                )
            )
            .all()
        )

    def exists_by_email(self, email: str) -> bool:
        return self.get_by_email(email) is not None

    # ==========================
    # UPDATE
    # ==========================

    def update(self, user: User) -> User:
        self.db.commit()
        self.db.refresh(user)
        return user

    def activate_user(self, user: User):
        user.is_active = True
        return self.update(user)

    def deactivate_user(self, user: User):
        user.is_active = False
        return self.update(user)

    # ==========================
    # DELETE
    # ==========================

    def delete(self, user: User):
        self.db.delete(user)
        self.db.commit()

    # ==========================
    # COUNT
    # ==========================

    def count(self) -> int:
        return self.db.query(User).count()

    # ==========================
    # PAGINATION
    # ==========================

    def paginate(
        self,
        skip: int = 0,
        limit: int = 20,
    ):
        return (
            self.db.query(User)
            .offset(skip)
            .limit(limit)
            .all()
        )