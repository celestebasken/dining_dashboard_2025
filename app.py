import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
@st.cache_data
def load_data():
    df = pd.read_csv("Data_for_dashboard.csv")
    df.columns = df.columns.str.strip()  # Remove extra spaces
    return df

df = load_data()

# Sustainability standards dictionary
sustainability_dict = {
    "OG": "USDA Organic",
    "CH": "Certified Humane",
    "FT": "Fair Trade Certified",
    "RAC": "Regenerative Agriculture Certification",
    "AGA": "American Grassfed Association",
    "AWA": "Animal Welfare Approved",
    "GAP": "Global Animal Partnership",
    "HFAC": "Humane Farm Animal Care",
    "MSC": "Marine Stewardship Council",
    "ASC": "Aquaculture Stewardship Council",
    "BAP": "Best Aquaculture Practices"
}

# Set up sidebar filters
st.sidebar.title("Filter Options")
categories = sorted(df['Category'].dropna().unique())
selected_category = st.sidebar.selectbox("Select Food Category", categories)

filtered_df = df[df['Category'] == selected_category]

campus_cols = ['UCLA', 'UCD_H', 'UCB', 'UCR', 'UCM', 'UCSC']
available_campuses = [col for col in campus_cols if col in filtered_df.columns]
selected_campus = st.sidebar.selectbox("Filter by Campus (optional)", ["All"] + available_campuses)

if selected_campus != "All":
    filtered_df = filtered_df[filtered_df[selected_campus] == 1]

sustainability_cols = ['OG', 'CH', 'FT', 'RAC', 'AGA', 'AWA', 'GAP', 'HFAC', 'MSC', 'ASC', 'BAP']
existing_standards = [col for col in sustainability_cols if col in filtered_df.columns]
selected_standard = st.sidebar.selectbox("Filter by Sustainability Standard (optional)", ["All"] + existing_standards)

if selected_standard != "All":
    filtered_df = filtered_df[filtered_df[selected_standard] == 1]

# MAIN PAGE
st.title("Institutional Food Purchasing Dashboard")

# Tool description
st.markdown("""
This dashboard allows users to explore institutional food procurement by category, supplier, distributor, and sustainability certifications.
Use the sidebar to filter for specific food categories, campuses, or sustainability standards.
""")

# Download button
st.download_button(
    label="📥 Download Full CSV",
    data=df.to_csv(index=False),
    file_name="Institutional_Food_Data.csv",
    mime="text/csv"
)

# Show filtered product table
st.subheader(f"Showing items in **{selected_category}**")
st.dataframe(filtered_df[['ProductName', 'Supplier', 'Distributor', 'Standard']])

# Horizontal bar chart of suppliers
st.subheader("Suppliers in Selected Category")
supplier_counts = filtered_df['Supplier'].value_counts()
fig, ax = plt.subplots()
supplier_counts.plot(kind='barh', ax=ax)
ax.set_xlabel("Number of Products")
ax.set_ylabel("Supplier")
st.pyplot(fig)

# Pie chart of sustainability standards
st.subheader("Sustainability Certifications in This Category")
standard_counts = {col: filtered_df[col].sum() for col in existing_standards}
standard_counts = {k: v for k, v in standard_counts.items() if v > 0}

if standard_counts:
    fig2, ax2 = plt.subplots()
    ax2.pie(standard_counts.values(), labels=standard_counts.keys(), autopct='%1.1f%%', startangle=90)
    ax2.axis('equal')
    st.pyplot(fig2)
else:
    st.write("No sustainability certifications found for this selection.")

# Sustainability dictionary
st.subheader("Sustainability Standards Glossary")
for acronym, definition in sustainability_dict.items():
    st.markdown(f"**{acronym}**: {definition}")
