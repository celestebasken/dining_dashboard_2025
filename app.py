import streamlit as st

st.set_page_config(page_title="UC Sustainable Procurement Dashboard", layout="wide")

st.sidebar.success("Select from the choices above")

st.title("UC Sustainable Procurement Dashboard")

st.markdown("""
Welcome to the UC Sustainable Procurement Dashboard!

This is a project of UC Berkeley Bonnie Reiss Global Food Initiative Fellows. This tool allows users to see what sustainable items are currently being purchased by UC campuses. It combines 
sustainable food purchasing data from multiple UC campuses, highlighting key attributes such as food category, supplier, distributor, and sustainability certifications. The data for this 
tool were kindly provided during the 2024-25 academic year by stakeholders from various campuses. 
            
It is our hope that this tool will help your campus to identify further opportunities to purchase sustainable products, in alignment with the UC Office of the President's goals.

### Use the menu on the left sidebar to:
- Search for food items by category, certification, campus, or region
- Explore supplier and distributor offerings
- View summaries of sustainability certifications

### What do we consider "Sustainable"
For the purposes of UCOP and the Bonnie Reiss fellowship, this database uses a narrow definition of sustainable.
- For most campuses, sustainable is defined by the Association for the Advancement of Sustainability in Higher 
Education's Sustainability Tracking, Assessment & Rating System (AASHE STARS). In short, this is a comprehensive list of standards
(with familiar names like USDA Organic, Fair Trade, etc) that they consider as sustainable.
- The only campuses that do not adhere to AASHE STARS are UC Health Campuses, which use Practice Greenhealth. Everything that is
considered sustainable under AASHE STARS is also counted under Pratice Greenhealth. 
- This database includes standards from BOTH. The only relevant standard in our guide that is ONLY sustainable under Practice Greenhealth
is Best Aquaculture Practices, or BAP.
            

            
---
This tool was created by Celeste Basken and Victoria Quach, 2025. For questions or feedback, please reach out to cbasken [at] berkeley [dot] edu. We would be very grateful for any 
feedback you have about features you would like to see, or bugs you spot. If you are a UC procurement stakeholder and would like to add or edit data, please also contact Celeste. Thanks!
""")

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
    "BAP": "Best Aquaculture Practices** not included in AASHE STARS",
    "MBA": "Monterrey Bay Aquarium"
}

existing_cols = [col for col in sustainability_dict if col in df.columns]
counts = {sustainability_dict[k]: df[k].sum() for k in existing_cols if df[k].sum() > 0}

# Glossary section
st.subheader("Glossary of Certification Terms")
for short, full in sustainability_dict.items():
    st.markdown(f"**{short}**: {full}")