
import os
import requests
from dotenv import load_dotenv

load_dotenv()
api_token = os.environ.get("linkedin_api")

def callout(title, location="", time_frame="24h", limit=10, description_format="text"):
    params = {"time_frame": time_frame, "limit": limit, "title": title, "description_format": description_format}
    if location:
        params["location"] = location
    r = requests.get(
        "https://data.fantastic.jobs/v1/active-ats",
        params=params,
        headers={"Authorization": f"Bearer {api_token}"},
        timeout=30,
    )
    r.raise_for_status()
    return r.json()