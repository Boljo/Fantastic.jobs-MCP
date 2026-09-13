from mcp.server.fastmcp import FastMCP
from client_call import callout

mcp = FastMCP("fantastic-jobs")

FIELDS = ["title", "organization", "url", "date_posted",
          "locations_derived", "ai_core_responsibilities", "description_text"]


@mcp.tool()
def search_jobs(title: str, location: str = "", time_frame: str = "24h", limit: int = 10, description_format: str = "text") -> list[dict]:
    """Search recent job postings from company career pages.
    title and location accept OR syntax, e.g. '"Software Engineer" OR "Data Scientist"'.
    location needs full names like 'New York, United States' (no abbreviations)."""
    return [{k: job.get(k) for k in FIELDS} for job in callout(title, location, time_frame, limit, description_format)]


if __name__ == "__main__":
    mcp.run()