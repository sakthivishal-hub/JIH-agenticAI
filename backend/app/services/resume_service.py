from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.repositories.resume_repository import ResumeRepository


class ResumeService:

    def __init__(self, db: Session):
        self.repository = ResumeRepository(db)

    def upload_resume(self, resume: Resume):
        return self.repository.create(resume)

    def get_resume(self, resume_id: int):
        return self.repository.get_by_id(resume_id)

    def get_user_resumes(self, user_id: int):
        return self.repository.get_by_user(user_id)

    def delete_resume(self, resume: Resume):
        self.repository.delete(resume)