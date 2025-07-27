import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Category Explorer", page_icon="📈")

st.sidebar.header("Interactive Tool")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("Data_for_dashboard.csv")
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

def list_campuses(row):
    campuses = [c for c in campus_cols if c in row and row[c] == 1]
    return ", ".join(campuses)

def list_tooltips(row):
    campuses = [c for c in campus_cols if c in row and row[c] == 1]
    return ", ".join([f"{c} ({campus_contacts[c]})" for c in campuses])

df['Campuses Procuring'] = df.apply(list_campuses, axis=1)
df['Campus Contacts'] = df.apply(list_tooltips, axis=1)

# Sustainability standard mapping
sustainability_dict = {
    "OG": "Organic",
    "CH": "Certified Humane",
    "FT": "Fair Trade",
    "RAC": "Regenerative Ag.",
    "AGA": "Grassfed Assoc.",
    "AWA": "Animal Welfare",
    "GAP": "Global Animal Partnership",
    "HFAC": "Humane Farm Care",
    "MSC": "Marine Stewardship Council",
    "ASC": "Aquaculture Stewardship Council",
    "BAP": "Best Aquaculture Practices"
}
sustainability_cols = [col for col in sustainability_dict if col in df.columns]

# Sidebar filters
st.sidebar.header("Filter Options")
categories = sorted(df['Category'].dropna().unique())
selected_category = st.sidebar.selectbox("Select Food Category", categories)
filtered_df = df[df['Category'] == selected_category]

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

# Fuzzy search
search_query = st.sidebar.text_input("Fuzzy Search (Product/Supplier)", "")
if search_query:
    def fuzzy_filter(row):
        name_score = difflib.SequenceMatcher(None, search_query.lower(), str(row['ProductName']).lower()).ratio()
        supplier_score = difflib.SequenceMatcher(None, search_query.lower(), str(row['Supplier']).lower()).ratio()
        return max(name_score, supplier_score) > 0.4
    filtered_df = filtered_df[filtered_df.apply(fuzzy_filter, axis=1)]


# Handle case when no data is returned
if filtered_df.empty:
    st.warning("No products found for the selected filters. Please try a different combination.")
else:
    # Show filtered data
    st.title("Filtered Product Table")
    st.dataframe(filtered_df[['ProductName', 'Supplier', 'Distributor', 'Standard', 'Campuses Procuring']])

    # Download CSV
    st.download_button("📥 Download Filtered CSV", data=filtered_df.to_csv(index=False), file_name="filtered_data.csv", mime="text/csv")

    # Horizontal bar chart
    st.subheader("Suppliers by Count")
    supplier_counts = filtered_df['Supplier'].value_counts()
    fig, ax = plt.subplots(figsize=(4, 3))
    supplier_counts.plot(kind='barh', ax=ax)
    ax.set_xlabel("Number of Products")
    ax.set_ylabel("Supplier")
    st.pyplot(fig)

    # Pie chart of sustainability certifications
    st.subheader("Sustainability Certifications")
    standard_counts = {sustainability_dict[k]: filtered_df[k].sum() for k in sustainability_cols if filtered_df[k].sum() > 0}
    if standard_counts:
        fig2, ax2 = plt.subplots(figsize=(2.5, 2.5))
        ax2.pie(standard_counts.values(), labels=standard_counts.keys(), autopct='%1.1f%%', startangle=90)
        ax2.axis('equal')
        st.pyplot(fig2)
    else:
        st.write("No sustainability certifications in this selection.")

