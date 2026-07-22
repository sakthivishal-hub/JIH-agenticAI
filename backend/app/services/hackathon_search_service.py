from tavily import TavilyClient

from app.core.config import settings


class HackathonSearchService:

    def __init__(self):
        self.client = TavilyClient(
            api_key=settings.TAVILY_API_KEY
        )

    def search_hackathons(self):

        query = """
        Find hackathons that are currently open for registration.

        Include:
        - Artificial Intelligence
        - Machine Learning
        - Data Science
        - Python
        - Web Development
        - Cyber Security
        - Cloud Computing

        Return only active hackathons.
        """

        response = self.client.search(
            query=query,
            search_depth="advanced",
            max_results=10,
            include_answer=True,
            include_raw_content=True,
        )

        return response