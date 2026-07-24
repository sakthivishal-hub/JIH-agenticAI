from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_active_user
from app.models.user import User
from app.schemas.user import UserResponse, UserUpdateRequest
from app.services.user_service import UserService
from pydantic import BaseModel

router = APIRouter()


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get Current User Profile",
)
def get_my_profile(
    current_user: User = Depends(get_current_active_user),
):
    return current_user


@router.put(
    "/me",
    response_model=UserResponse,
    summary="Update Current User Profile",
)
def update_my_profile(
    request: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = UserService(db)

    try:
        updated_user = service.update_profile(
            user=current_user,
            name=request.name,
            email=request.email,
        )

        return updated_user

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/change-password",
    summary="Change Password",
)
def change_password(
    request: ChangePasswordRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    service = UserService(db)

    try:
        service.change_password(
            user=current_user,
            current_password=request.current_password,
            new_password=request.new_password,
        )

        return {
            "message": "Password changed successfully"
        }

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )