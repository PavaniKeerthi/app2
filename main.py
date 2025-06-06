from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
import requests
from urllib.parse import urlparse
import json

app = FastAPI()


def extract_github_username(value: str) -> str:
    if "github.com" in value:
        return urlparse(value).path.strip("/")
    return value


@app.get("/analyze/github/{username}")
def analyze_github(username: str):
    url = f"https://api.github.com/users/{username}"
    r = requests.get(url)
    if r.status_code == 200:
        data = r.json()
        return {
            "Username": username,
            "Profile URL": data.get("html_url", ""),
            "Public Repos": data.get("public_repos", 0),
            "Followers": data.get("followers", 0),
            "Following": data.get("following", 0),
            "Status": "✅ Found"
        }
    else:
        return {
            "Username": username,
            "Profile URL": f"https://github.com/{username}",
            "Public Repos": "N/A",
            "Followers": "N/A",
            "Following": "N/A",
            "Status": "❌ Not Found"
        }


class LeetCodeRequest(BaseModel):
    url: str


@app.post("/analyze/leetcode/")
def analyze_leetcode(request: LeetCodeRequest):
    try:
        username = request.url.strip("/").split("/")[-1]
        api_url = "https://leetcode.com/graphql/"
        headers = {"Content-Type": "application/json"}
        payload = {
            "query": """
            query getUserProfile($username: String!) {
              matchedUser(username: $username) {
                submitStats: submitStatsGlobal {
                  acSubmissionNum {
                    difficulty
                    count
                  }
                }
              }
            }
            """,
            "variables": {"username": username}
        }
        r = requests.post(api_url, headers=headers, data=json.dumps(payload))
        data = r.json()
        stats = data["data"]["matchedUser"]["submitStats"]["acSubmissionNum"]
        return {
            "Username": username,
            "Profile URL": f"https://leetcode.com/{username}/",
            "Total Solved": sum(item["count"] for item in stats if item["difficulty"] != "All"),
            "Easy Solved": next((item["count"] for item in stats if item["difficulty"] == "Easy"), 0),
            "Medium Solved": next((item["count"] for item in stats if item["difficulty"] == "Medium"), 0),
            "Hard Solved": next((item["count"] for item in stats if item["difficulty"] == "Hard"), 0),
            "Status": "✅ Found"
        }
    except Exception:
        return {
            "Username": username,
            "Profile URL": request.url,
            "Total Solved": "N/A",
            "Easy Solved": "N/A",
            "Medium Solved": "N/A",
            "Hard Solved": "N/A",
            "Status": "❌ Not Found"
        }
