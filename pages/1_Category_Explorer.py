import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Category Explorer", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("Data_for_dashboard.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# Campus hover info
campus_cols = ['UCLA', 'UCD_H', 'UCB', 'UCR', 'UCM', 'UCSC']
campus_contacts = {
    "UCLA": "UCLA - Jane Doe (jane.doe@ucla.edu)",
    "UCD_H": "UC Davis - John Smith (john.smith@ucd.edu)",
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
    return ", ".join([campus_contacts[c] for c in campuses])

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

campus = st.sidebar.selectbox("Filter by Campus", ["All"] + campus_cols)
if campus != "All":
    filtered_df = filtered_df[filtered_df[campus] == 1]

cert = st.sidebar.selectbox("Filter by Sustainability Standard", ["All"] + sustainability_cols)
if cert != "All":
    filtered_df = filtered_df[filtered_df[cert] == 1]

# Download CSV
st.download_button("📥 Download Filtered CSV", data=filtered_df.to_csv(index=False), file_name="filtered_data.csv", mime="text/csv")

# Show filtered data
st.title("Filtered Product Table")
with st.expander("View Table"):
    st.dataframe(filtered_df[['Product Name', 'Supplier', 'Distributor', 'Standard', 'Campuses Procuring']])

# Horizontal bar chart
st.subheader("Suppliers by Count")
supplier_counts = filtered_df['Supplier'].value_counts()
fig, ax = plt.subplots()
supplier_counts.plot(kind='barh', ax=ax)
ax.set_xlabel("Number of Products")
ax.set_ylabel("Supplier")
st.pyplot(fig)

# Pie chart of sustainability certifications
st.subheader("Sustainability Certifications")
standard_counts = {sustainability_dict[k]: filtered_df[k].sum() for k in sustainability_cols if filtered_df[k].sum() > 0}
if standard_counts:
    fig2, ax2 = plt.subplots()
    ax2.pie(standard_counts.values(), labels=standard_counts.keys(), autopct='%1.1f%%', startangle=90)
    ax2.axis('equal')
    st.pyplot(fig2)
else:
    st.write("No sustainability certifications in this selection.")
