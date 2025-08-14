import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import difflib
import os, requests
from io import StringIO

if st.session_state.get("authentication_status") != True:
    st.info("Please log in on the main page to continue.")
    st.stop()

st.set_page_config(page_title="Sustainability Stats", page_icon="📈")

st.sidebar.header("Sustainability Stats")

# Load data
@st.cache_data(show_spinner=False)
def load_data():
    url = os.getenv(
        "CSV_GDRIVE_URL",
        "https://docs.google.com/spreadsheets/d/1qsapyNmZleoL75aIwH57W3nqTc_VLhdbFEieOTwYWiI/export?format=csv&gid=0",
    )
    r = requests.get(url, timeout=30)
    r.raise_for_status()

    # If Drive returns an HTML login/permission page:
    if r.text.lstrip().startswith("<"):
        st.error("Google Sheets returned HTML (permissions?). Share the sheet as 'Anyone with the link: Viewer'.")
        return pd.DataFrame()

    df = pd.read_csv(StringIO(r.text))
    df.columns = df.columns.str.strip()
    return df

# Load once per page run (or share via session_state below)
if "df" not in st.session_state:
    st.session_state["df"] = load_data()

df = st.session_state["df"]

# Optional: stop gracefully if nothing loaded
if df.empty:
    st.warning("No data loaded from Google Sheets. Check the CSV link or permissions.")
    st.stop()

st.title("Sustainability Certifications Overview")

sustainability_dict = {
    "OG": "Organic",
    "CH": "Certified Humane",
    "FT": "Fair Trade",
    "RAC": "Regenerative Ag.",
    "AGA": "Grassfed Assoc.",
    "AWA": "Animal Welfare",
    "GAP": "Global Animal Partnership",
    "AHC": "American Humane Certified",
    "HFAC": "Humane Farm Care",
    "MSC": "Marine Stewardship Council",
    "BAP": "Best Aquaculture Practices",
    "MBA": "Monterrey Bay Aquarium"
}

existing_cols = [col for col in sustainability_dict if col in df.columns]
counts = {sustainability_dict[k]: df[k].sum() for k in existing_cols if df[k].sum() > 0}

# Horizontal bar chart
st.subheader("Distribution of Certifications Across All Products")
if counts:
    fig, ax = plt.subplots(figsize=(3, 2))
    ax.barh(list(counts.keys()), list(counts.values()))
    ax.set_xlabel("Number of Products")
    ax.set_ylabel("Certification")
    st.pyplot(fig)
else:
    st.write("No sustainability certifications found.")


