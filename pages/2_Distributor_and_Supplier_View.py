import streamlit as st
import pandas as pd

if st.session_state.get("authentication_status") != True:
    st.info("Please log in on the main page to continue.")
    st.stop()

st.set_page_config(page_title="Distributor & Supplier View", layout="wide")

# Load data
@st.cache_data
def load_data():
    # Prefer env var on Render; fallback to hardcoded CSV export link
    url = os.getenv(
        "CSV_GDRIVE_URL",
        "https://docs.google.com/spreadsheets/d/1qsapyNmZleoL75aIwH57W3nqTc_VLhdbFEieOTwYWiI/export?format=csv&gid=0"
    )

    try:
        r = requests.get(url, timeout=30)
        r.raise_for_status()

        # If permissions aren’t public, Drive may return HTML. Guard against that:
        if r.text.lstrip().startswith("<"):
            st.error("Google Sheets returned HTML (likely a permissions issue). Make sure the sheet is shared as 'Anyone with the link: Viewer'.")
            return pd.DataFrame()

        df = pd.read_csv(StringIO(r.text))
        df.columns = df.columns.str.strip()
        return df

    except Exception as e:
        st.error(f"Failed to load data: {e}")
        return pd.DataFrame()

# Campus mapping and helpers
campus_name_map = {
    "UCLA": "UCLA",
    "UCD_H": "UC Davis Health",
    "UCB": "UC Berkeley",
    "UCR": "UC Riverside",
    "UCM": "UC Merced",
    "UCSC": "UC Santa Cruz"
}
campus_cols = list(campus_name_map.keys())

def list_campuses(row):
    campuses = [c for c in campus_cols if c in row and row[c] == 1]
    return ", ".join([campus_name_map[c] for c in campuses])

df['Campuses Procuring'] = df.apply(list_campuses, axis=1)

st.markdown("""
# Distributor and Supplier View
Use this page to explore the sustainable offerings that distributors and suppliers are providing to UC campuses.
""")

st.title("Explore by Distributor")

distributors = sorted(df['Distributor'].dropna().unique())
selected_distributor = st.selectbox("Select a Distributor", distributors, key="distributor_select")

dist_df = df[df['Distributor'] == selected_distributor]
if dist_df.empty:
    st.warning("No products found for this distributor.")
else:
    st.subheader(f"Suppliers Provided by {selected_distributor}")
    suppliers = sorted(dist_df['Supplier'].dropna().unique())
    st.write(", ".join(suppliers))

    campuses_procuring = [campus_name_map[c] for c in campus_cols if c in dist_df.columns and dist_df[c].sum() > 0]
    st.subheader(f"Campuses Purchasing from {selected_distributor}")
    if campuses_procuring:
        st.write(", ".join(campuses_procuring))
    else:
        st.write("No campus purchases found for this distributor.")

    st.subheader("Products from This Distributor")
    st.dataframe(dist_df[['ProductName', 'Supplier', 'Category', 'Standard', 'Campuses Procuring']])

    st.download_button(
        label="📥 Download Distributor Products",
        data=dist_df.to_csv(index=False),
        file_name=f"{selected_distributor.replace(' ', '_')}_products.csv",
        mime="text/csv"
    )

st.markdown("---")

st.title("Explore by Supplier")

suppliers = sorted(df['Supplier'].dropna().unique())
selected_supplier = st.selectbox("Select a Supplier", suppliers, key="supplier_select")

supp_df = df[df['Supplier'] == selected_supplier]
if supp_df.empty:
    st.warning("No products found for this supplier.")
else:
    st.subheader(f"Distributors That Carry {selected_supplier}")
    distros = sorted(supp_df['Distributor'].dropna().unique())
    st.write(", ".join(distros))

    campuses_procuring = [campus_name_map[c] for c in campus_cols if c in supp_df.columns and supp_df[c].sum() > 0]
    st.subheader(f"Campuses Purchasing from {selected_supplier}")
    if campuses_procuring:
        st.write(", ".join(campuses_procuring))
    else:
        st.write("No campus purchases found for this supplier.")

    st.subheader("Products from This Supplier")
    st.dataframe(supp_df[['ProductName', 'Distributor', 'Category', 'Standard', 'Campuses Procuring']])

    st.download_button(
        label="📥 Download Supplier Products",
        data=supp_df.to_csv(index=False),
        file_name=f"{selected_supplier.replace(' ', '_')}_products.csv",
        mime="text/csv"
    )
