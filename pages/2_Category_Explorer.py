import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import difflib

if st.session_state.get("authentication_status") != True:
    st.info("Please log in on the main page to continue.")
    st.stop()

st.set_page_config(page_title="Category Explorer", page_icon="📈")

st.sidebar.header("Interactive Tool")

# Load data from public Google Sheet
@st.cache_data
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1qsapyNmZleoL75aIwH57W3nqTc_VLhdbFEieOTwYWiI/export?format=csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# Region mapping
region_map = {
    "SoCal": ["UCLA", "UCR"],
    "Central": ["UCM"],
    "NorCal": ["UCB", "UCD_H", "UCSC"]
}

campus_cols = ['UCLA', 'UCD_H', 'UCB', 'UCR', 'UCM', 'UCSC']
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

def list_campuses(row):
    campuses = [c for c in campus_cols if c in row and row[c] == 1]
    return ", ".join(campuses)

def list_tooltips(row):
    campuses = [c for c in campus_cols if c in row and row[c] == 1]
    return ", ".join([f"{c} ({campus_contacts[c]})" for c in campuses])

def list_full_campuses(row):
    campuses = [c for c in campus_cols if c in row and row[c] == 1]
    return ", ".join([campus_name_map[c] for c in campuses])

df['Campuses Procuring'] = df.apply(list_campuses, axis=1)
df['Campus Contacts'] = df.apply(list_tooltips, axis=1)
df['Full Campus Names'] = df.apply(list_full_campuses, axis=1)

# Sustainability standard mapping
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
sustainability_cols = [col for col in sustainability_dict if col in df.columns]

# Sidebar filters
st.sidebar.header("Filter Options")
categories = ["All"] + sorted(df['Category'].dropna().unique())
selected_category = st.sidebar.selectbox("Select Food Category", categories)
filtered_df = df if selected_category == "All" else df[df['Category'] == selected_category]

# Region filter
regions = list(region_map.keys())
selected_region = st.sidebar.selectbox("Filter by Region", ["All"] + regions)
if selected_region != "All":
    region_campuses = region_map[selected_region]
    filtered_df = filtered_df[filtered_df[region_campuses].sum(axis=1) > 0]

# Campus filter
campus = st.sidebar.selectbox("Filter by Campus", ["All"] + campus_cols)
if campus != "All":
    filtered_df = filtered_df[filtered_df[campus] == 1]

# Certification filter
cert = st.sidebar.selectbox("Filter by Sustainability Standard", ["All"] + sustainability_cols)
if cert != "All":
    filtered_df = filtered_df[filtered_df[cert] == 1]

st.markdown("""
## Product Explorer
Use the menu on the left to search for sustainable food items by category, campus region, campus, or sustainability certification.
- The default view is all sustainable products that UC campuses shared with our team, so it is quite large.
- All products that appear in the table below are certified sustainable per AASHE STARS or Practice Greenhealth. Please click on 
the app tab to learn more about sustainability certifications
- You can download the current table view with the "Download Filtered CSV" button
""")

# Handle case when no data is returned
if filtered_df.empty:
    st.warning("No products found for the selected filters. Please try a different combination.")
else:
    st.title("Filtered Product Table")
    st.dataframe(filtered_df[['ProductName', 'Supplier', 'Distributor', 'Standard', 'Campuses Procuring']])

    st.download_button("📥 Download Filtered CSV", data=filtered_df.to_csv(index=False), file_name="filtered_data.csv", mime="text/csv")

    st.subheader("Suppliers Providing These Products")
    unique_suppliers = sorted(filtered_df['Supplier'].dropna().unique())
    st.write(", ".join(unique_suppliers))

    st.subheader("Campuses Purchasing These Products")
    campus_names = set()
    for row in filtered_df.itertuples():
        if hasattr(row, 'Full_Campus_Names'):
            campus_names.update([x.strip() for x in getattr(row, 'Full_Campus_Names').split(',') if x.strip()])
        else:
            campus_names.update([campus_name_map[c] for c in campus_cols if getattr(row, c) == 1])
    if campus_names:
        st.write(", ".join(sorted(campus_names)))
    else:
        st.write("No campus purchases found in this selection.")

    # Horizontal bar chart of sustainability certifications
    st.subheader("Sustainability Certifications")
    standard_counts = {sustainability_dict[k]: filtered_df[k].sum() for k in sustainability_cols if filtered_df[k].sum() > 0}
    if standard_counts:
        fig2, ax2 = plt.subplots(figsize=(4, 3))
        ax2.barh(list(standard_counts.keys()), list(standard_counts.values()))
        ax2.set_xlabel("Number of Products")
        ax2.set_ylabel("Certification")
        st.pyplot(fig2)
    else:
        st.write("No sustainability certifications in this selection.")
