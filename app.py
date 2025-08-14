# app.py  (MAIN PAGE)

import os, yaml, requests
from io import StringIO
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
import time

# ---- MUST be first Streamlit call ----
st.set_page_config(page_title="UC Sustainable Procurement Dashboard", layout="wide")

# ---- Auth config (prefer ENV, fallback inline for local) ----
INLINE_AUTH_YAML = """
credentials:
  usernames:
    analyst:
      email: cbasken@berkeley.edu
      password: $2b$12$3zAuuEeiJZKalDszyb.9aOrQzT/QxCb.qNvdffdYdRIYBP0BD3Eby
    viewer:
      email: viewer@example.com
      password: $2b$12$3zAuuEeiJZKalDszyb.9aOrQzT/QxCb.qNvdffdYdRIYBP0BD3Eby
cookie:
  name: st_auth_cookie
  key: _qbVFRIvRxtW1iSMBQXoUB80tFpxtjBAfnvdPN5VX28
  expiry_days: 7
preauthorized:
  emails: []
""".strip()

auth_yaml = os.getenv("AUTH_CONFIG_YAML", INLINE_AUTH_YAML).strip()
config = yaml.load(auth_yaml, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    cookie_expiry_days=config["cookie"]["expiry_days"],
    auto_hash=False,   # we supplied bcrypt hashes in YAML
)

# ---- Login ----
result = authenticator.login(
    location="main",
    fields={"Form name": "Login", "Username": "Username", "Password": "Password", "Login": "Login"},
)
if result is None:
    st.stop()
name, auth_status, username = result
st.session_state["authentication_status"] = auth_status

if auth_status is False:
    st.error("Invalid username or password")
    st.stop()
elif auth_status is None:
    st.info("Please enter your username and password")
    st.stop()

# ---- Logged in UI ----
with st.sidebar:
    authenticator.logout("Logout", "sidebar")

# --- minimal landing so it's never blank ---
st.title("UC Sustainable Procurement Dashboard")
st.write("Welcome! Use the sidebar Pages menu, or jump in below:")

# Links to pages (works even if data fails to load)
st.page_link("pages/1_Category_Explorer.py", label="📊 Category Explorer")
st.page_link("pages/2_Distributor_Supplier_View.py", label="🏷️ Distributor & Supplier View")
st.page_link("pages/3_Sustainability_Stats.py", label="🌿 Sustainability Stats")

st.title("UC Sustainable Procurement Dashboard")

st.markdown("""
Welcome to the UC Sustainable Procurement Dashboard!  
(…your intro text…)
""")

# ---- Data loader used by the landing page only ----
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

df = load_data()
if df.empty:
    st.warning("No data loaded yet. Check the CSV link or permissions.")
else:
    sustainability_dict = {
        "OG": "Organic", "CH": "Certified Humane", "FT": "Fair Trade",
        "RAC": "Regenerative Ag.", "AGA": "Grassfed Assoc.", "AWA": "Animal Welfare",
        "GAP": "Global Animal Partnership", "AHC": "American Humane Certified",
        "HFAC": "Humane Farm Care", "MSC": "Marine Stewardship Council",
        "BAP": "Best Aquaculture Practices** not included in AASHE STARS",
        "MBA": "Monterrey Bay Aquarium",
    }
    existing_cols = [c for c in sustainability_dict if c in df.columns]
    counts = {sustainability_dict[c]: int(df[c].sum()) for c in existing_cols if df[c].sum() > 0}

    st.subheader("Sustainability Certifications Overview")
    if counts:
        st.write("\n".join(f"- **{k}**: {v}" for k, v in counts.items()))
    else:
        st.write("No certification counts available for the current data.")

# Glossary section
st.subheader("Glossary of Certification Terms")
for short, full in sustainability_dict.items():
    st.markdown(f"**{short}**: {full}")
st.markdown("""
---
This tool was created by Celeste Basken and Victoria Quach, 2025. For questions or feedback, please reach out to cbasken [at] berkeley [dot] edu. 
We would be very grateful for any feedback you have about features you would like to see, or bugs you spot. Thanks! :-)
""")
