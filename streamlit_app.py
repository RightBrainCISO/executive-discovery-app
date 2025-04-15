
import streamlit as st
import pandas as pd
import requests
import time

st.title("🔎 Executive Discovery App")
st.markdown("Upload a list of companies and find executive/board members with titles and LinkedIn URLs.")

uploaded_file = st.file_uploader("📤 Upload your company list (CSV with 'Company Name' column)", type="csv")
api_key = st.text_input("🔐 Enter your PhantomBuster API Key", type="password")

def generate_queries(df):
    titles = ["CEO", "Founder", "President", "Board Member"]
    df["LinkedIn Search Query"] = df["Company Name"].apply(
        lambda c: f'site:linkedin.com/in "{c}" ({" OR ".join(f"\"{t}\"" for t in titles)})'
    )
    return df

if uploaded_file and api_key:
    df = pd.read_csv(uploaded_file)
    df = generate_queries(df)
    st.dataframe(df[["Company Name", "LinkedIn Search Query"]])

    if st.button("🚀 Launch PhantomBuster Search Export"):
        headers = {
            "X-Phantombuster-Key-1": api_key,
            "Content-Type": "application/json",
        }

        agent_id = st.text_input("🔧 Enter your Phantom ID for LinkedIn Search Export")

        if agent_id:
            launch_url = "https://api.phantombuster.com/api/v2/agents/launch"
            launch_body = {"id": agent_id}
            r = requests.post(launch_url, headers=headers, json=launch_body)

            if r.status_code == 200:
                st.success("✅ Phantom launched successfully! Polling for results...")
                container = st.empty()
                result_url = f"https://api.phantombuster.com/api/v2/agents/fetch-output?id={agent_id}"

                for _ in range(30):
                    time.sleep(10)
                    res = requests.get(result_url, headers=headers)
                    if res.status_code == 200 and res.json().get("container"):
                        data = res.json()["container"]
                        profiles = pd.DataFrame(data)
                        st.success("🎯 Results received!")
                        st.dataframe(profiles[["name", "jobTitle", "linkedinUrl"]])
                        st.download_button("📥 Download Results as CSV", profiles.to_csv(index=False), "executives.csv")
                        break
                    container.info("⏳ Waiting for PhantomBuster to return data...")
            else:
                st.error("❌ Failed to launch Phantom. Check your API key and agent ID.")
