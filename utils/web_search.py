from langchain_community.utilities import SerpAPIWrapper
from config.config import SERP_API_KEY


def web_search(query):

    if not query:
        return "No query provided."

    try:

        search = SerpAPIWrapper(
            serpapi_api_key=SERP_API_KEY,
            params={
                "engine": "google",
                "num": 5
            }
        )

        results = search.results(query)

        if "organic_results" not in results:
            return "No web results found."

        formatted_results = []

        for r in results["organic_results"][:5]:

            title = r.get("title", "")
            snippet = r.get("snippet", "")
            link = r.get("link", "")

            formatted_results.append(
                f"**{title}**\n{snippet}\n{link}"
            )

        return "\n\n".join(formatted_results)

    except Exception as e:
        return f"Web search error: {str(e)}"