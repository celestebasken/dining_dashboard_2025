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

---
This tool was created by Celeste Basken and Victoria Quach, 2025. For questions or feedback, please reach out to cbasken [at] berkeley [dot] edu. We would be very grateful for any 
feedback you have about features you would like to see, or bugs you spot. If you are a UC procurement stakeholder and would like to add or edit data, please also contact Celeste. Thanks!
""")
