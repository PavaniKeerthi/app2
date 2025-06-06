from fastapi import FastAPI
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
    try:
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        return {
            "Username": username,
            "Profile URL": data.get("html_url", ""),
            "Public Repos": data.get("public_repos", 0),
            "Followers": data.get("followers", 0),
            "Following": data.get("following", 0),
            "Status": "✅ Found"
        }
    except Exception as e:
        return {
            "Username": username,
            "Profile URL": f"https://github.com/{username}",
            "Public Repos": "N/A",
            "Followers": "N/A",
            "Following": "N/A",
            "Status": f"❌ Request Failed: {str(e)}"
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

        r = requests.post(api_url, headers=headers, data=json.dumps(payload), timeout=10)
        r.raise_for_status()
        data = r.json()

        if not data.get("data") or not data["data"].get("matchedUser"):
            raise ValueError("User not found")

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
    except Exception as e:
        return {
            "Username": request.url,
            "Profile URL": request.url,
            "Total Solved": "N/A",
            "Easy Solved": "N/A",
            "Medium Solved": "N/A",
            "Hard Solved": "N/A",
            "Status": f"❌ Request Failed: {str(e)}"
        }
