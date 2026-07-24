from enum import Enum


# =========================
# Authentication
# =========================
class TokenType(str, Enum):
    BEARER = "bearer"


# =========================
# User Roles
# =========================
class UserRole(str, Enum):
    STUDENT = "student"
    ADMIN = "admin"


# =========================
# Opportunity Types
# =========================
class OpportunityType(str, Enum):
    JOB = "Job"
    INTERNSHIP = "Internship"
    HACKATHON = "Hackathon"
    RESEARCH = "Research"
    SCHOLARSHIP = "Scholarship"
    COMPETITION = "Competition"


# =========================
# Work Mode
# =========================
class WorkMode(str, Enum):
    REMOTE = "Remote"
    HYBRID = "Hybrid"
    ONSITE = "Onsite"


# =========================
# Match Levels
# =========================
class MatchLevel(str, Enum):
    EXCELLENT = "Excellent"
    GOOD = "Good"
    AVERAGE = "Average"
    LOW = "Low"


# =========================
# API Messages
# Enums instead of plain dicts -> typos caught before runtime (e.g.
# ERROR["USER_NOT_FOUD"] fails silently as a dict; ErrorMsg.USER_NOT_FOUD
# fails immediately with autocomplete warning you first)
# =========================
class SuccessMsg(str, Enum):
    REGISTER = "User registered successfully."
    LOGIN = "Login successful."
    PROFILE_UPDATED = "Profile updated successfully."
    RESUME_UPLOADED = "Resume uploaded successfully."
    OPPORTUNITY_FOUND = "Opportunities retrieved successfully."
    MATCHES_COMPUTED = "Matches computed successfully."
    NOTIFICATION_SENT = "Notification sent successfully."


class ErrorMsg(str, Enum):
    INVALID_CREDENTIALS = "Invalid email or password."
    USER_EXISTS = "User already exists."
    USER_NOT_FOUND = "User not found."
    UNAUTHORIZED = "Unauthorized access."
    FORBIDDEN = "You do not have permission to perform this action."
    TOKEN_EXPIRED = "Access token has expired."
    INVALID_TOKEN = "Invalid access token."
    SERVER_ERROR = "Internal server error."
    VALIDATION_ERROR = "Validation failed."
    FILE_TOO_LARGE = "Uploaded file exceeds the maximum allowed size."
    INVALID_FILE_TYPE = "Unsupported file type."
    RESUME_PARSE_FAILED = "Could not parse the uploaded resume."
    OPPORTUNITY_NOT_FOUND = "Opportunity not found."


# =========================
# AI Configuration
# Weights must sum to 100 -- asserted below so a typo in one weight
# can't silently break the scoring model at runtime.
# =========================
AI_SCORE = {
    "SKILL_MATCH": 35,
    "LOCATION_MATCH": 15,
    "CAREER_GROWTH": 15,
    "ROI": 10,
    "REPUTATION": 10,
    "LEARNING": 5,
    "COMPETITION": 5,
    "DEADLINE": 5,
}
assert sum(AI_SCORE.values()) == 100, "AI_SCORE weights must sum to 100"

MATCH_LEVEL_THRESHOLDS = {
    MatchLevel.EXCELLENT: 80,
    MatchLevel.GOOD: 60,
    MatchLevel.AVERAGE: 40,
    MatchLevel.LOW: 0,
}


def score_to_match_level(score: float) -> MatchLevel:
    """Converts a 0-100 AI match score into a MatchLevel label."""
    for level, threshold in MATCH_LEVEL_THRESHOLDS.items():
        if score >= threshold:
            return level
    return MatchLevel.LOW


# =========================
# Upload Configuration
# =========================
ALLOWED_RESUME_EXTENSIONS = {".pdf", ".doc", ".docx"}
ALLOWED_RESUME_MIME_TYPES = {
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}
MAX_RESUME_SIZE_MB = 10
MAX_RESUME_SIZE_BYTES = MAX_RESUME_SIZE_MB * 1024 * 1024