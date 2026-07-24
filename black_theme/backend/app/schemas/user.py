from pydantic import BaseModel, EmailStr


class UserUpdateRequest(BaseModel):
    name: str | None = None
    email: EmailStr | None = None

    college: str | None = None
    degree: str | None = None
    branch: str | None = None
    year: int | None = None

    skills: str | None = None
    interests: str | None = None
    preferred_role: str | None = None
    preferred_location: str | None = None
    current_location: str | None = None

    linkedin_url: str | None = None
    github_url: str | None = None
    portfolio_url: str | None = None

    bio: str | None = None


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    is_active: bool

    class Config:
        from_attributes = True