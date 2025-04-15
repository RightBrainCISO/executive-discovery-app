# Executive Discovery App

This Streamlit app lets you:
- Upload a list of company names
- Generate valid LinkedIn search URLs
- Use PhantomBuster to scrape profiles
- View/export enriched data

## Setup

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Secrets
Create `.streamlit/secrets.toml`:

```toml
[phantombuster]
api_key = "YOUR_PHANTOMBUSTER_API_KEY"
phantom_id = "YOUR_PHANTOM_ID"
```
