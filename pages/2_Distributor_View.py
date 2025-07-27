import streamlit as st
import pandas as pd

st.set_page_config(page_title="View by Distributor", page_icon="📈")

st.markdown("# Another title space")
st.sidebar.header("View by Distributor")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("Data_for_dashboard.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

st.title("Explore by Distributor")

# List of all distributors
distributors = sorted(df['Distributor'].dropna().unique())
selected_distributor = st.selectbox("Select a Distributor", distributors)

dist_df = df[df['Distributor'] == selected_distributor]
suppliers = sorted(dist_df['Supplier'].dropna().unique())

# Summary
st.markdown(f"""
### Distributor: `{selected_distributor}`
- **Total Products**: {len(dist_df)}
- **Suppliers:** {len(suppliers)}
""")

# List suppliers
st.subheader("Suppliers Provided by This Distributor")
st.write(", ".join(suppliers))

# Show mini table
st.subheader("Products Provided by This Distributor")
st.dataframe(dist_df[['Product Name', 'Supplier', 'Category', 'Standard']])

# Optional download button
st.download_button(
    label="📥 Download This Distributor's Products",
    data=dist_df.to_csv(index=False),
    file_name=f"{selected_distributor.replace(' ', '_')}_products.csv",
    mime="text/csv"
)
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Distributor View", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("Data_for_dashboard.csv")
    df.columns = df.columns.str.strip()
    return df

df = load_data()

st.title("Explore by Distributor")

# List of all distributors
distributors = sorted(df['Distributor'].dropna().unique())
selected_distributor = st.selectbox("Select a Distributor", distributors)

dist_df = df[df['Distributor'] == selected_distributor]
suppliers = sorted(dist_df['Supplier'].dropna().unique())

# Summary
st.markdown(f"""
### Distributor: `{selected_distributor}`
- **Total Products**: {len(dist_df)}
- **Suppliers:** {len(suppliers)}
""")

# List suppliers
st.subheader("Suppliers Provided by This Distributor")
st.write(", ".join(suppliers))

# Show mini table
st.subheader("Products Provided by This Distributor")
st.dataframe(dist_df[['Product Name', 'Supplier', 'Category', 'Standard']])

# Optional download button
st.download_button(
    label="📥 Download This Distributor's Products",
    data=dist_df.to_csv(index=False),
    file_name=f"{selected_distributor.replace(' ', '_')}_products.csv",
    mime="text/csv"
)
