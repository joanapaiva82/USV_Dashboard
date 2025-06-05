import streamlit as st
import pandas as pd

# --- Setup page ---
st.set_page_config(page_title="Global USV's Dashboard", layout="wide")
st.title("📊 Global USV's Dashboard – Excel Viewer")

with st.expander("📌 Disclaimer (click to expand)"):
    st.markdown("""
    The information presented on this page has been compiled solely for **academic and research purposes** in support of a postgraduate dissertation in **MSc Hydrography at the University of Plymouth**.

    All specifications, features, and descriptions of Uncrewed Surface Vessels (USVs) are based on **publicly available sources** and **have not been independently verified**.

    **⚠️ This content is not intended to serve as an official or authoritative source.**  
    Do not rely on this data for operational, procurement, or technical decisions.  
    Please consult the original manufacturers for validated information.

    ---
    **Author:** Joana Paiva  
    **Email:** [joana.paiva82@outlook.com](mailto:joana.paiva82@outlook.com)
    """)

# --- Load Excel ---
df = pd.read_excel("USVs_Summary_improve.xlsx", engine="openpyxl")
df = df.dropna(how="all")
df.columns = df.columns.str.strip()

# --- Reset trigger
if "reset_counter" not in st.session_state:
    st.session_state.reset_counter = 0

# --- Sidebar Filters ---
with st.sidebar:
    st.subheader("🔎 Keyword Filters")

    # Reset button
    if st.button("🔄 Clear All Filters"):
        st.session_state.global_keyword = ""
        st.session_state.reset_counter += 1

    # Global keyword
    global_keyword = st.text_input("🌐 Global Keyword (search all fields)", key=f"global_keyword_{st.session_state.reset_counter}")

    # Define field layout groups for side-by-side filters
    grouped_fields = [
        ("Name", "Manufacturer"),
        ("Country", None),
        ("Min. Speed (Knots)", "Max Speed (Knots)"),
        ("Speed Description", None),
        ("Min. Endurance (Days)", "Max. Endurance (Days)"),
        ("Min. Endurance (Hours)", "Max. Endurance (Hours)"),
        ("Endurance Description", None),
        ("Max. Length (m)", "Full Dimensions (L×W×H)"),
        ("Propulsion", "Power"),
        ("Sensors", "Main Application"),
        ("Comms", "Sensor Suite"),
        ("Communication", "Crew Requirement"),
        ("Certifications", "MASS Level"),
        ("Use Cases", None),
        ("Pros", "Cons"),
        ("Spec Sheet (URL)", None),
        ("Source URL", "Sources")
    ]

    dropdown_filters = {}
    for field1, field2 in grouped_fields:
        if field2:
            col1, col2 = st.columns(2)
            with col1:
                if field1 in df.columns:
                    opts = sorted(df[field1].dropna().unique().tolist())
                    sel = st.multiselect(field1, opts, default=[], key=f"{field1}_{st.session_state.reset_counter}")
                    if sel: dropdown_filters[field1] = sel
            with col2:
                if field2 in df.columns:
                    opts = sorted(df[field2].dropna().unique().tolist())
                    sel = st.multiselect(field2, opts, default=[], key=f"{field2}_{st.session_state.reset_counter}")
                    if sel: dropdown_filters[field2] = sel
        else:
            if field1 in df.columns:
                opts = sorted(df[field1].dropna().unique().tolist())
                sel = st.multiselect(field1, opts, default=[], key=f"{field1}_{st.session_state.reset_counter}")
                if sel: dropdown_filters[field1] = sel

# --- Filtering Logic ---
filtered_df = df.copy()

# Global keyword filter
if global_keyword:
    keyword = global_keyword.lower()
    mask = filtered_df.apply(lambda row: row.astype(str).str.lower().str.contains(keyword).any(), axis=1)
    filtered_df = filtered_df[mask]

# Column filters
for col, selected_vals in dropdown_filters.items():
    filtered_df = filtered_df[
        filtered_df[col].astype(str).apply(lambda x: any(val.lower() in x.lower() for val in selected_vals))
    ]

# --- Spec Sheet clickable
link_config = {}
if "Spec Sheet (URL)" in df.columns:
    link_config["Spec Sheet (URL)"] = st.column_config.LinkColumn(
        label="Spec Sheet (URL)",
        help="Click to open manufacturer spec sheet"
    )

# --- Display Results ---
st.markdown(f"Loaded `{filtered_df.shape[0]}` rows × `{filtered_df.shape[1]}` columns")
st.markdown("### 📋 Filtered Results (Click 'Spec Sheet' to view links)")
st.dataframe(filtered_df, use_container_width=True, column_config=link_config)
