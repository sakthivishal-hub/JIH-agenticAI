from pydantic import BaseModel


class OpportunitySavePayload(BaseModel):
    """Shape of a single opportunity as returned by /opportunities/search,
    /recommendations, /hackathons/search or /research/search -- sent back
    by the frontend so it can be upserted into the DB and bookmarked."""

    title: str
    company: str | None = ""
    location: str | None = ""
    salary: str | None = ""
    deadline: str | None = None
    apply_link: str
    description: str | None = ""
    skills: list[str] | str | None = None
    source: str | None = "unknown"
    type: str | None = "unknown"
