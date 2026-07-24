
from sqlalchemy.orm import Session

from app.core.security import (
    create_access_token,
    hash_password,
    verify_password,
)
from app.models.user import User
from app.repositories.user_repository import UserRepository



class AuthService:

    def __init__(self, db: Session):
        self.repository = UserRepository(db)

    def register(
        self,
        name: str,
        email: str,
        password: str,
    ):
        if self.repository.get_by_email(email):
            raise ValueError("Email already exists")
        hashed = hash_password(password)

        user = User(
            name=name,
            email=email,
            password_hash=hashed,
        )
        return self.repository.create(user)


    def login(
        self,
        email: str,
        password: str,
        )-> str | None:
        print("login email:",email)
        user = self.repository.get_by_email(email)
        print("user found:",user)
        if user is None:
            return None
        print("HASH IN DB:", user.password_hash)
        if not verify_password(
            password,
            user.password_hash,
        ):

            return None

        return create_access_token(
            {"sub": str(user.id)}
        )