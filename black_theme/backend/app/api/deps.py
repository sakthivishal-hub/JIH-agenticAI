from types import SimpleNamespace


async def get_current_user():
    return SimpleNamespace(
        id=1,
        email="demo@example.com",
        role="student",
        resume_text="",
        skills="",
    )