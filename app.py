# app.py — minimal, known-good auth + landing

import os, yaml
import streamlit as st
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader
import time

st.set_page_config(page_title="UC Sustainable Procurement Dashboard", layout="wide")

# --- Auth config: prefer ENV on Render; fallback inline for local ---
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
    auto_hash=False,  # we already provide bcrypt hashes
)

# --- Login UI ---
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

# --- Logged-in landing (always renders something) ---
with st.sidebar:
    authenticator.logout("Logout", "sidebar")

st.title("UC Sustainable Procurement Dashboard")
st.write("Welcome! Use the links below to navigate:")

st.page_link("pages/1_Category_Explorer.py", label="📊 Category Explorer")
st.page_link("pages/2_Distributor_Supplier_View.py", label="🏷️ Distributor & Supplier View")
st.page_link("pages/3_Sustainability_Stats.py", label="🌿 Sustainability Stats")


# Glossary section
st.subheader("Glossary of Certification Terms")
for short, full in sustainability_dict.items():
    st.markdown(f"**{short}**: {full}")
st.markdown("""
---
This tool was created by Celeste Basken and Victoria Quach, 2025. For questions or feedback, please reach out to cbasken [at] berkeley [dot] edu. 
We would be very grateful for any feedback you have about features you would like to see, or bugs you spot. Thanks! :-)
""")
