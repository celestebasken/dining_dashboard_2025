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
@st.cache_data(show_spinner=False, ttl=600)
def load_data():
    url = os.getenv(
        "CSV_GDRIVE_URL",
        "https://docs.google.com/spreadsheets/d/1qsapyNmZleoL75aIwH57W3nqTc_VLhdbFEieOTwYWiI/export?format=csv&gid=0",
    )
    headers = {"User-Agent": "Mozilla/5.0"}  # helps avoid some 400s/blocks
    last_err = None

    for attempt in range(3):  # simple retry
        try:
            r = requests.get(url, headers=headers, timeout=30)
            if r.status_code == 200:
                # If Drive returned an HTML page (permissions/login), don't crash
                if r.text.lstrip().startswith("<"):
                    st.error("Google Sheets returned HTML (likely permissions). Share as 'Anyone with the link: Viewer'.")
                    return pd.DataFrame()
                df = pd.read_csv(StringIO(r.text))
                df.columns = df.columns.str.strip()
                return df
            else:
                last_err = f"HTTP {r.status_code}"
        except Exception as e:
            last_err = str(e)
        time.sleep(1.5 * (attempt + 1))  # backoff

    st.error(f"Failed to fetch CSV from Google Sheets. {last_err or ''} "
             f"Check the URL & gid, and that sharing is 'Anyone with the link: Viewer'.")
    return pd.DataFrame()

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