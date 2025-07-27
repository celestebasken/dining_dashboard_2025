import streamlit as st

st.set_page_config(page_title="UC Sustainable Procurement Dashboard", layout="wide")

st.sidebar.success("Select from the choices above")

st.title("UC Sustainable Procurement Dashboard")

st.markdown("""
Welcome to the UC Sustainable Procurement Dashboard!

This tool allows users to explore food purchasing data from multiple campuses and institutions, highlighting
key attributes such as food category, suppliers, distributors, and sustainability certifications.

### Use the menu on the left sidebar to:
- Browse food products by category
- Explore supplier and distributor relationships
- View summaries of sustainability certifications

---
Created by Celeste Basken, 2025. For questions or feedback, please reach out to cbasken [at] berkeley [dot] edu.
""")
