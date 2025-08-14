import os, yaml, streamlit as st, streamlit_authenticator as stauth
import requests
from io import StringIO
import pandas as pd
from yaml.loader import SafeLoader

# Prefer ENV; allow inline only as a local fallback
INLINE_AUTH_YAML = """
credentials:
  usernames:
    analyst:
      email: cbasken@berkeley.edu
      hashed_password: $2b$12$3zAuuEeiJZKalDszyb.9aOrQzT/QxCb.qNvdffdYdRIYBP0BD3Eby
    viewer:
      email: viewer@example.com
      hashed_password: $2b$12$3zAuuEeiJZKalDszyb.9aOrQzT/QxCb.qNvdffdYdRIYBP0BD3Eby
cookie:
  name: st_auth_cookie
  key: _qbVFRIvRxtW1iSMBQXoUB80tFpxtjBAfnvdPN5VX28
  expiry_days: 7
preauthorized:
  emails: []
""".strip()

auth_yaml = os.getenv("AUTH_CONFIG_YAML", INLINE_AUTH_YAML).strip()

try:
    config = yaml.load(auth_yaml, Loader=SafeLoader)
except Exception as e:
    st.error(f"Auth config error: {e}")
    st.stop()

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    cookie_expiry_days=config["cookie"]["expiry_days"],
    auto_hash=False,  # you already provided bcrypt hashes
)

if "auth_status" not in st.session_state:
    st.session_state["auth_status"] = None

name, auth_status, username = authenticator.login(
    location="main",
    fields={
        "Form name": "Login",
        "Username": "Username",
        "Password": "Password",
        "Login": "Login",
    },
)

if auth_status is False:
    st.error("Invalid username or password, please try again or contact Celeste for help")
    st.stop()
elif auth_status is None:
    st.info("Please enter your username and password")
    st.stop()
else:
    with st.sidebar:
        authenticator.logout("Logout", "sidebar")

# === Done ===

st.set_page_config(page_title="UC Sustainable Procurement Dashboard", layout="wide")

st.sidebar.success("Select from the choices above")

st.title("UC Sustainable Procurement Dashboard")

st.markdown("""
Welcome to the UC Sustainable Procurement Dashboard!

This is a project of UC Berkeley Bonnie Reiss Global Food Initiative Fellows. This tool allows users to see what sustainable items are currently being purchased by UC campuses. It combines 
sustainable food purchasing data from multiple UC campuses, highlighting key attributes such as food category, supplier, distributor, and sustainability certifications. The data for this 
tool were kindly provided during the 2024-25 academic year by stakeholders from various campuses. If you are a UC procurement stakeholder 
and would like to add or edit data, please contact Celeste (information below).
            
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
considered sustainable under AASHE STARS is also counted under Pratice Greenhealth. However, there are some standards included in Practice
Greenhealth that are not part of AASHE STARS.
- This database includes standards from BOTH. The only relevant standard in our guide that is ONLY sustainable under Practice Greenhealth
is Best Aquaculture Practices, or BAP. (BAP is not part of STARS)
            
""")

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
st.markdown("""
---
This tool was created by Celeste Basken and Victoria Quach, 2025. For questions or feedback, please reach out to cbasken [at] berkeley [dot] edu. 
We would be very grateful for any feedback you have about features you would like to see, or bugs you spot. Thanks! :-)
""")
