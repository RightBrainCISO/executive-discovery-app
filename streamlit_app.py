import streamlit as st
import pandas as pd
import requests
import time
import urllib.parse

st.title("🔎 Executive Discovery App")
st.markdown("Upload a list of companies and find executive/board members with titles and LinkedIn URLs.")

uploaded_file = st.file_uploader("📤 Upload your company list (CSV with 'Company Name' column)", type="csv")
api_key = st.secrets["phantombuster"]["api_key"]
phantom_id = st.secrets["phantombuster"]["phantom_id"]

def generate_search_urls(df):
    titles = ["CEO", "Founder", "President", "Board Member"]
    def make_url(company):
        query = f'{company} ' + ' OR '.join(titles)
        encoded = urllib.parse.quote(query)
        return f'https://www.linkedin.com/search/results/people/?keywords={encoded}'
    df["LinkedIn Search URL"] = df["Company Name"].apply(make_url)
    return df

if uploaded_file:
    df = pd.read_csv(uploaded_file)
    df = generate_search_urls(df)
    st.dataframe(df[["Company Name", "LinkedIn Search URL"]])

    if st.button("🚀 Launch PhantomBuster Search Export"):
        headers = {
            "X-Phantombuster-Key-1": api_key,
            "Content-Type": "application/json",
        }
        search_urls = df["LinkedIn Search URL"].tolist()
        launch_url = "https://api.phantombuster.com/api/v2/agents/launch"
        launch_body = {
            "id": phantom_id,
            "argument": {
                "searchUrls": search_urls
            }
        }
        r = requests.post(launch_url, headers=headers, json=launch_body)

        if r.status_code == 200:
            st.success("✅ Phantom launched successfully! Polling for results...")
            container = st.empty()
            result_url = f"https://api.phantombuster.com/api/v2/agents/fetch-output?id={phantom_id}"

            for _ in range(30):
                time.sleep(10)
                res = requests.get(result_url, headers=headers)
                if res.status_code == 200 and res.json().get("container"):
                    data = res.json()["container"]
                    profiles = pd.DataFrame(data)
                    st.success("🎯 Results received!")
                    st.dataframe(profiles)
                    st.download_button("📥 Download Results as CSV", profiles.to_csv(index=False), "executives.csv")
                    break
                container.info("⏳ Waiting for PhantomBuster to return data...")
        else:
            st.error("❌ Failed to launch Phantom. Check your API key and Phantom ID.")
