import streamlit as st

st.set_page_config(page_title="Institutional Food Dashboard", layout="wide")

st.write("# Test Title Location")

st.sidebar.success("Select a demo above")

st.title("Institutional Food Purchasing Dashboard")

st.markdown("""
Welcome to the Institutional Food Procurement Dashboard!

This tool allows users to explore food purchasing data from multiple campuses and institutions, highlighting
key attributes such as food category, suppliers, distributors, and sustainability certifications.

### Use the Pages menu (left sidebar) to:
- Browse food products by category
- Explore supplier and distributor relationships
- View summaries of sustainability certifications

---
Created by [Your Name], 2025. For questions or feedback, please reach out to [your.email@example.com].
""")
