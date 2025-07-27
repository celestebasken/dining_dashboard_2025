import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Sustainability Stats", page_icon="📈")

st.sidebar.header("Sustainability Stats")

@st.cache_data
def load_data():
    df = pd.read_csv("Data_for_dashboard.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

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

# Glossary section
st.subheader("Glossary of Certification Terms")
for short, full in sustainability_dict.items():
    st.markdown(f"**{short}**: {full}")
