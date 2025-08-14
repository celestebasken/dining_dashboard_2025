# pages/1_Category_Explorer.py

import os, requests
from io import StringIO
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import difflib

# --- require login ---
if st.session_state.get("authentication_status") != True:
    st.info("Please log in on the main page to continue.")
    st.stop()

st.sidebar.header("Interactive Tool")

# --- data loader (same as app.py) ---
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

# share loaded df across pages
if "df" not in st.session_state:
    st.session_state["df"] = load_data()
df = st.session_state["df"]

if df.empty:
    st.warning("No data loaded from Google Sheets. Check the CSV link or permissions.")
    st.stop()

# --------- schema guards / defaults ----------
# Campus columns we expect as 0/1 flags
campus_cols = ['UCLA', 'UCD_H', 'UCB', 'UCR', 'UCM', 'UCSC']
for c in campus_cols:
    if c not in df.columns:
        df[c] = 0

# Some sheets call it 'Standard' or 'Standards'
if "Standard" not in df.columns:
    if "Standards" in df.columns:
        df["Standard"] = df["Standards"]
    else:
        df["Standard"] = ""

# Product name column guard
if "ProductName" not in df.columns:
    # try common alternatives
    for alt in ["Product Name", "Product", "Item"]:
        if alt in df.columns:
            df.rename(columns={alt: "ProductName"}, inplace=True)
            break

# Category guard
if "Category" not in df.columns:
    st.error("Your sheet is missing a 'Category' column.")
    st.stop()

# Certification columns we tally (create missing as 0)
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
for k in sustainability_dict:
    if k not in df.columns:
        df[k] = 0

# --------- helpers ----------
campus_contacts = {
    "UCLA": "UCLA - Jane Doe (jane.doe@ucla.edu)",
    "UCD_H": "UC Davis Health - John Smith (john.smith@ucd.edu)",
    "UCB": "UC Berkeley - Alex Kim (alex.kim@berkeley.edu)",
    "UCR": "UC Riverside - Maria Lopez (maria.lopez@ucr.edu)",
    "UCM": "UC Merced - Omar Patel (omar.patel@ucmerced.edu)",
    "UCSC": "UC Santa Cruz - Riley Nguyen (riley.nguyen@ucsc.edu)"
}
campus_name_map = {
    "UCLA": "UCLA",
    "UCD_H": "UC Davis Health",
    "UCB": "UC Berkeley",
    "UCR": "UC Riverside",
    "UCM": "UC Merced",
    "UCSC": "UC Santa Cruz"
}
region_map = {"SoCal": ["UCLA", "UCR"], "Central": ["UCM"], "NorCal": ["UCB", "UCD_H", "UCSC"]}

def list_campuses(row):
    campuses = [c for c in campus_cols if c in row and row[c] == 1]
    return ", ".join(campuses)

def list_tooltips(row):
    campuses = [c for c in campus_cols if c in row and row[c] == 1]
    return ", ".join([f"{c} ({campus_contacts[c]})" for c in campuses])

def list_full_campuses(row):
    campuses = [c for c in campus_cols if c in row and row[c] == 1]
    return ", ".join([campus_name_map[c] for c in campuses])

# derived columns (idempotent)
if "Campuses Procuring" not in df.columns:
    df["Campuses Procuring"] = df.apply(list_campuses, axis=1)
if "Campus Contacts" not in df.columns:
    df["Campus Contacts"] = df.apply(list_tooltips, axis=1)
if "Full Campus Names" not in df.columns:
    df["Full Campus Names"] = df.apply(list_full_campuses, axis=1)

# --------- sidebar filters ----------
st.sidebar.header("Filter Options")
categories = ["All"] + sorted(df["Category"].dropna().astype(str).unique().tolist())
selected_category = st.sidebar.selectbox("Select Food Category", categories)
filtered_df = df if selected_category == "All" else df[df["Category"] == selected_category]

regions = list(region_map.keys())
selected_region = st.sidebar.selectbox("Filter by Region", ["All"] + regions)
if selected_region != "All":
    region_campuses = region_map[selected_region]
    # guard in case any campus col missing
    region_campuses = [c for c in region_campuses if c in filtered_df.columns]
    if region_campuses:
        filtered_df = filtered_df[filtered_df[region_campuses].sum(axis=1) > 0]

campus = st.sidebar.selectbox("Filter by Campus", ["All"] + campus_cols)
if campus != "All" and campus in filtered_df.columns:
    filtered_df = filtered_df[filtered_df[campus] == 1]

sustainability_cols = [c for c in sustainability_dict.keys() if c in filtered_df.columns]
cert = st.sidebar.selectbox("Filter by Sustainability Standard", ["All"] + sustainability_cols)
if cert != "All":
    filtered_df = filtered_df[filtered_df[cert] == 1]

# --------- page body ----------
st.markdown("""
## Product Explorer
Use the menu on the left to search for sustainable food items by category, campus region, campus, or sustainability certification.
- The default view shows all rows shared with our team, so it may be large.
- You can download the current table view with the **Download Filtered CSV** button.
""")

if filtered_df.empty:
    st.warning("No products found for the selected filters. Please try a different combination.")
    st.stop()

st.title("Filtered Product Table")

# only select columns that actually exist
cols_to_show = [c for c in ["ProductName", "Supplier", "Distributor", "Standard", "Campuses Procuring"] if c in filtered_df.columns]
st.dataframe(filtered_df[cols_to_show])

st.download_button(
    "📥 Download Filtered CSV",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_data.csv",
    mime="text/csv",
)

st.subheader("Suppliers Providing These Products")
unique_suppliers = sorted(filtered_df.get("Supplier", pd.Series(dtype=str)).dropna().astype(str).unique().tolist())
st.write(", ".join(unique_suppliers) if unique_suppliers else "—")

st.subheader("Campuses Purchasing These Products")
campus_names = set()
for row in filtered_df.itertuples(index=False):
    if "Full Campus Names" in filtered_df.columns:
        campus_names.update([x.strip() for x in getattr(row, "_asdict", lambda: {})().get("Full Campus Names", "").split(",") if x.strip()] if hasattr(row, "_asdict") else [])
    else:
        for c in campus_cols:
            try:
                if getattr(row, c) == 1:
                    campus_names.add(campus_name_map[c])
            except AttributeError:
                pass
st.write(", ".join(sorted(campus_names)) if campus_names else "—")

st.subheader("Sustainability Certifications")
standard_counts = {sustainability_dict[k]: int(filtered_df[k].sum()) for k in sustainability_cols if k in filtered_df.columns and filtered_df[k].sum() > 0}
if standard_counts:
    fig2, ax2 = plt.subplots(figsize=(4, 3))
    ax2.barh(list(standard_counts.keys()), list(standard_counts.values()))
    ax2.set_xlabel("Number of Products")
    ax2.set_ylabel("Certification")
    st.pyplot(fig2)
else:
    st.write("No sustainability certifications in this selection.")
