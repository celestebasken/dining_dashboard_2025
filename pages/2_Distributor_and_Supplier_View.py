import os, requests
from io import StringIO
import pandas as pd
import streamlit as st
import time

# --- require login ---
if st.session_state.get("authentication_status") != True:
    st.info("Please log in on the main page to continue.")
    st.stop()

st.markdown("# Distributor and Supplier View")
st.caption("Use this page to explore the sustainable offerings that distributors and suppliers are providing to UC campuses.")

# --- data loader (same pattern as app.py) ---
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

# --- schema guards / sane defaults ---
campus_name_map = {
    "UCLA": "UCLA",
    "UCD_H": "UC Davis Health",
    "UCB": "UC Berkeley",
    "UCR": "UC Riverside",
    "UCM": "UC Merced",
    "UCSC": "UC Santa Cruz",
}
campus_cols = list(campus_name_map.keys())
for c in campus_cols:
    if c not in df.columns:
        df[c] = 0

# Ensure expected key columns exist
for col in ["Distributor", "Supplier", "Category"]:
    if col not in df.columns:
        df[col] = ""

# Canonicalize Standard column
if "Standard" not in df.columns:
    if "Standards" in df.columns:
        df["Standard"] = df["Standards"]
    else:
        df["Standard"] = ""

# Derived helper
def list_campuses(row):
    campuses = [c for c in campus_cols if c in row and row[c] == 1]
    return ", ".join([campus_name_map[c] for c in campuses])

if "Campuses Procuring" not in df.columns:
    df["Campuses Procuring"] = df.apply(list_campuses, axis=1)

# ========================
# Explore by Distributor
# ========================
st.subheader("Explore by Distributor")

distributors = sorted(df["Distributor"].dropna().astype(str).unique().tolist())
if not distributors:
    st.info("No distributors found in the dataset.")
    st.stop()

selected_distributor = st.selectbox("Select a Distributor", distributors, key="distributor_select")

dist_df = df[df["Distributor"] == selected_distributor]
if dist_df.empty:
    st.warning("No products found for this distributor.")
else:
    st.markdown(f"**Suppliers provided by {selected_distributor}:**")
    suppliers = sorted(dist_df["Supplier"].dropna().astype(str).unique().tolist())
    st.write(", ".join(suppliers) if suppliers else "—")

    campuses_procuring = [campus_name_map[c] for c in campus_cols if c in dist_df.columns and dist_df[c].sum() > 0]
    st.markdown(f"**Campuses purchasing from {selected_distributor}:**")
    st.write(", ".join(campuses_procuring) if campuses_procuring else "—")

    st.markdown("**Products from this distributor**")
    cols_to_show = [c for c in ["ProductName", "Supplier", "Category", "Standard", "Campuses Procuring"] if c in dist_df.columns]
    st.dataframe(dist_df[cols_to_show])

    st.download_button(
        label="📥 Download Distributor Products",
        data=dist_df.to_csv(index=False),
        file_name=f"{selected_distributor.replace(' ', '_')}_products.csv",
        mime="text/csv",
    )

st.markdown("---")

# ========================
# Explore by Supplier
# ========================
st.subheader("Explore by Supplier")

suppliers_all = sorted(df["Supplier"].dropna().astype(str).unique().tolist())
if not suppliers_all:
    st.info("No suppliers found in the dataset.")
    st.stop()

selected_supplier = st.selectbox("Select a Supplier", suppliers_all, key="supplier_select")

supp_df = df[df["Supplier"] == selected_supplier]
if supp_df.empty:
    st.warning("No products found for this supplier.")
else:
    st.markdown(f"**Distributors that carry {selected_supplier}:**")
    distros = sorted(supp_df["Distributor"].dropna().astype(str).unique().tolist())
    st.write(", ".join(distros) if distros else "—")

    campuses_procuring = [campus_name_map[c] for c in campus_cols if c in supp_df.columns and supp_df[c].sum() > 0]
    st.markdown(f"**Campuses purchasing from {selected_supplier}:**")
    st.write(", ".join(campuses_procuring) if campuses_procuring else "—")

    st.markdown("**Products from this supplier**")
    cols_to_show = [c for c in ["ProductName", "Distributor", "Category", "Standard", "Campuses Procuring"] if c in supp_df.columns]
    st.dataframe(supp_df[cols_to_show])

    st.download_button(
        label="📥 Download Supplier Products",
        data=supp_df.to_csv(index=False),
        file_name=f"{selected_supplier.replace(' ', '_')}_products.csv",
        mime="text/csv",
    )
