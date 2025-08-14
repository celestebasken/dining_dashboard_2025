# pages/3_Sustainability_Stats.py

import os, requests
from io import StringIO
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

# --- require login ---
if st.session_state.get("authentication_status") != True:
    st.info("Please log in on the main page to continue.")
    st.stop()

st.sidebar.header("Sustainability Stats")
st.title("Sustainability Certifications Overview")

# --- data loader (same pattern as other pages) ---
@st.cache_data(show_spinner=False)
def load_data():
    url = os.getenv(
        "CSV_GDRIVE_URL",
        "https://docs.google.com/spreadsheets/d/1qsapyNmZleoL75aIwH57W3nqTc_VLhdbFEieOTwYWiI/export?format=csv&gid=0",
    )
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    if r.text.lstrip().startswith("<"):
        st.error("Google Sheets returned HTML (check sharing: 'Anyone with the link: Viewer').")
        return pd.DataFrame()
    df = pd.read_csv(StringIO(r.text))
    df.columns = df.columns.str.strip()
    return df

# share df across pages
if "df" not in st.session_state:
    st.session_state["df"] = load_data()
df = st.session_state["df"]

if df.empty:
    st.warning("No data loaded from Google Sheets. Check the CSV link or permissions.")
    st.stop()

# --- certification dictionary & guards ---
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
    "MBA": "Monterrey Bay Aquarium",
}

# ensure missing cert columns exist; coerce to numeric
for k in sustainability_dict:
    if k not in df.columns:
        df[k] = 0
    df[k] = pd.to_numeric(df[k], errors="coerce").fillna(0)

# build counts, drop zeros, sort descending
counts = {sustainability_dict[k]: int(df[k].sum()) for k in sustainability_dict if df[k].sum() > 0}
counts = dict(sorted(counts.items(), key=lambda x: x[1], reverse=True))

st.subheader("Distribution of Certifications Across All Products")
if counts:
    fig, ax = plt.subplots(figsize=(4, 3))  # modest size
    ax.barh(list(counts.keys())[::-1], list(counts.values())[::-1])  # largest on top
    ax.set_xlabel("Number of Products")
    ax.set_ylabel("Certification")
    st.pyplot(fig)
else:
    st.write("No sustainability certifications found in the current dataset.")

# optional: quick table view
with st.expander("See counts as a table"):
    st.dataframe(pd.DataFrame.from_dict(counts, orient="index", columns=["Count"]))