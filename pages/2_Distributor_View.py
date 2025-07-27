import streamlit as st
import pandas as pd

st.set_page_config(page_title="Distributor & Supplier View", layout="wide")

@st.cache_data
def load_data():
    df = pd.read_csv("Data_for_dashboard.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

st.title("Explore by Distributor")

distributors = sorted(df['Distributor'].dropna().unique())
selected_distributor = st.selectbox("Select a Distributor", distributors, key="distributor_select")

dist_df = df[df['Distributor'] == selected_distributor]
if dist_df.empty:
    st.warning("No products found for this distributor.")
else:
    st.subheader(f"Suppliers Provided by {selected_distributor}")
    suppliers = sorted(dist_df['Supplier'].dropna().unique())
    st.write(", ".join(suppliers))

    st.subheader("Products from This Distributor")
    st.dataframe(dist_df[['ProductName', 'Supplier', 'Category', 'Standard']])

    st.download_button(
        label="📥 Download Distributor Products",
        data=dist_df.to_csv(index=False),
        file_name=f"{selected_distributor.replace(' ', '_')}_products.csv",
        mime="text/csv"
    )

st.markdown("---")

st.title("Explore by Supplier")

suppliers = sorted(df['Supplier'].dropna().unique())
selected_supplier = st.selectbox("Select a Supplier", suppliers, key="supplier_select")

supp_df = df[df['Supplier'] == selected_supplier]
if supp_df.empty:
    st.warning("No products found for this supplier.")
else:
    st.subheader(f"Distributors That Carry {selected_supplier}")
    distros = sorted(supp_df['Distributor'].dropna().unique())
    st.write(", ".join(distros))

    st.subheader("Products from This Supplier")
    st.dataframe(supp_df[['ProductName', 'Distributor', 'Category', 'Standard']])

    st.download_button(
        label="📥 Download Supplier Products",
        data=supp_df.to_csv(index=False),
        file_name=f"{selected_supplier.replace(' ', '_')}_products.csv",
        mime="text/csv"
    )
