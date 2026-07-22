from sqlalchemy.orm import Session

from app.core.security import (
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository


class UserService:

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    # ==========================
    # CREATE
    # ==========================

    def create_user(self, user: User):
        return self.repository.create(user)

    # ==========================
    # READ
    # ==========================

    def get_user(self, user_id: int):
        return self.repository.get_by_id(user_id)

    def get_user_by_email(self, email: str):
        return self.repository.get_by_email(email)

    def get_all_users(self):
        return self.repository.get_all()

    # ==========================
    # UPDATE
    # ==========================

    def update_profile(
        self,
        user: User,
        name: str | None = None,
        email: str | None = None,
    ):
        if name is not None:
            user.name = name

        if email is not None:
            existing = self.repository.get_by_email(email)

            if existing and existing.id != user.id:
                raise ValueError("Email already exists")

            user.email = email

        return self.repository.update(user)

    def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ):
        if not verify_password(
            current_password,
            user.password_hash,
        ):
            raise ValueError("Current password is incorrect")

        user.password_hash = hash_password(new_password)

        return self.repository.update(user)

    # ==========================
    # DELETE
    # ==========================

    def delete_user(self, user: User):
        self.repository.delete(user)