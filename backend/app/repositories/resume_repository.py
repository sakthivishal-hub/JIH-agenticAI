from typing import Optional

from sqlalchemy.orm import Session

from app.models.resume import Resume


class ResumeRepository:
    """
    Handles all database operations for Resume.
    """

    def __init__(self, db: Session):
        self.db = db

    # ==========================
    # CREATE
    # ==========================

    def create(self, resume: Resume) -> Resume:
        self.db.add(resume)
        self.db.commit()
        self.db.refresh(resume)
        return resume

    # ==========================
    # READ
    # ==========================

    def get_by_id(self, resume_id: int) -> Optional[Resume]:
        return (
            self.db.query(Resume)
            .filter(Resume.id == resume_id)
            .first()
        )

    def get_all(self):
        return (
            self.db.query(Resume)
            .order_by(Resume.id.desc())
            .all()
        )

    def get_by_user(self, user_id: int):
        return (
            self.db.query(Resume)
            .filter(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
            .all()
        )

    def get_latest_resume(self, user_id: int):
        return (
            self.db.query(Resume)
            .filter(Resume.user_id == user_id)
            .order_by(Resume.created_at.desc())
            .first()
        )

    # ==========================
    # UPDATE
    # ==========================

    def update(self, resume: Resume) -> Resume:
        self.db.commit()
        self.db.refresh(resume)
        return resume

    def update_summary(
        self,
        resume: Resume,
        summary: str,
    ):
        resume.summary = summary
        return self.update(resume)

    def update_skills(
        self,
        resume: Resume,
        skills: str,
    ):
        resume.skills = skills
        return self.update(resume)

    def update_resume_score(
        self,
        resume: Resume,
        score: int,
    ):
        resume.resume_score = score
        return self.update(resume)

    # ==========================
    # DELETE
    # ==========================

    def delete(self, resume: Resume):
        self.db.delete(resume)
        self.db.commit()

    def delete_by_user(self, user_id: int):
        (
            self.db.query(Resume)
            .filter(Resume.user_id == user_id)
            .delete()
        )
        self.db.commit()

    # ==========================
    # COUNT
    # ==========================

    def count(self):
        return self.db.query(Resume).count()

    # ==========================
    # PAGINATION
    # ==========================

    def paginate(
        self,
        skip: int = 0,
        limit: int = 20,
    ):
        return (
            self.db.query(Resume)
            .offset(skip)
            .limit(limit)
            .all()
        )