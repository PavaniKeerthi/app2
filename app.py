import streamlit as st
import pandas as pd
import requests
from urllib.parse import urlparse

st.set_page_config(page_title="Profile Analyzer", layout="centered")
st.title("🔍 GitHub & LeetCode Profile Analyzer")

uploaded_file = st.file_uploader("Upload your CSV", type=["csv"])
platform = st.selectbox("Select Platform", ["GitHub", "LeetCode"])

column_map = {
    "GitHub": "This is my GitHub ID",
    "LeetCode": "Paste your Leetcode profile link"
}

FASTAPI_URL = "https://your-fastapi-service.onrender.com"

def extract_github_username(value):
    if "github.com" in value:
        return urlparse(value).path.strip("/")
    return value

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    col = column_map[platform]

    if col not in df.columns:
        st.error(f"CSV must contain the column: {col}")
    else:
        st.success(f"Analyzing {platform} profiles...")
        results = []

        for val in df[col].dropna():
            try:
                if platform == "GitHub":
                    username = extract_github_username(val)
                    res = requests.get(f"{FASTAPI_URL}/analyze/github/{username}")
                    results.append(res.json())

                elif platform == "LeetCode":
                    payload = {"url": val}
                    res = requests.post(f"{FASTAPI_URL}/analyze/leetcode/", json=payload)
                    results.append(res.json())

            except Exception as e:
                results.append({
                    "Username": val,
                    "Error": str(e),
                    "Status": "❌ Request Failed"
                })

        df_results = pd.DataFrame(results)
        st.dataframe(df_results)

        csv = df_results.to_csv(index=False)
        st.download_button("Download Results as CSV", csv, file_name="profile_analysis.csv", mime="text/csv")
