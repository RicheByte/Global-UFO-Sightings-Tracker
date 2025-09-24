import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from streamlit_folium import st_folium

# --- Configuration ---
st.set_page_config(layout="wide", page_title="Global UFO Sightings Tracker")

# --- Helper Functions ---
@st.cache_data(ttl=3600) # Cache data for 1 hour
def load_data(db_path='ufo_sightings.db'):
    """Loads data from SQLite database."""
    conn = sqlite3.connect(db_path)
    df = pd.read_sql_query("SELECT * FROM sightings", conn)
    conn.close()
    
    df['datetime'] = pd.to_datetime(df['datetime'])
    df['date'] = pd.to_datetime(df['date'])
    df['year'] = df['date'].dt.year
    return df

def create_map(filtered_df):
    """Creates a Folium map with clustered markers."""
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="CartoDB DarkMatter")
    
    if not filtered_df.empty:
        marker_cluster = MarkerCluster().add_to(m)
        for idx, row in filtered_df.iterrows():
            if pd.notna(row['latitude']) and pd.notna(row['longitude']):
                popup_html = f"""
                <b>Date:</b> {row['date'].strftime('%Y-%m-%d')}<br>
                <b>Location:</b> {row['city'].title() if pd.notna(row['city']) else 'N/A'}, {row['state'].upper() if pd.notna(row['state']) else 'N/A'}, {row['country'].upper() if pd.notna(row['country']) else 'N/A'}<br>
                <b>Shape:</b> {row['shape'].title()}<br>
                <b>Description:</b> {row['description'][:200]}...
                """
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=folium.Popup(popup_html, max_width=300),
                    tooltip=f"{row['city'].title()}, {row['shape'].title()}"
                ).add_to(marker_cluster)
    return m

# --- Load Data ---
df = load_data()

# Get min/max years for slider
min_year = int(df['year'].min())
max_year = int(df['year'].max())

# --- Streamlit UI ---
st.title("👽 Global UFO Sightings Tracker")

# Sidebar for Filters
st.sidebar.header("Filter Sightings")

# Date Range Slider
year_range = st.sidebar.slider(
    "Select Year Range",
    min_value=min_year,
    max_value=max_year,
    value=(min_year, max_year)
)
filtered_df = df[(df['year'] >= year_range[0]) & (df['year'] <= year_range[1])]

# Country Filter
all_countries = sorted(filtered_df['country'].dropna().unique())
selected_countries = st.sidebar.multiselect("Filter by Country", all_countries)
if selected_countries:
    filtered_df = filtered_df[filtered_df['country'].isin(selected_countries)]

# State Filter (only if countries are selected or for US/Canada)
if 'us' in filtered_df['country'].str.lower().unique() or 'ca' in filtered_df['country'].str.lower().unique() or selected_countries:
    all_states = sorted(filtered_df['state'].dropna().unique())
    selected_states = st.sidebar.multiselect("Filter by State (if applicable)", all_states)
    if selected_states:
        filtered_df = filtered_df[filtered_df['state'].isin(selected_states)]

# Shape Filter
all_shapes = sorted(filtered_df['shape'].dropna().unique())
selected_shapes = st.sidebar.multiselect("Filter by Shape", all_shapes)
if selected_shapes:
    filtered_df = filtered_df[filtered_df['shape'].isin(selected_shapes)]

# Keyword Search
keyword = st.sidebar.text_input("Search in Description (e.g., 'bright light')")
if keyword:
    filtered_df = filtered_df[filtered_df['description'].str.contains(keyword, case=False, na=False)]

st.sidebar.markdown(f"**Total Sightings (Filtered):** {len(filtered_df):,}")

# --- Main Content ---
col1, col2 = st.columns([3, 1])

with col1:
    st.subheader("UFO Sightings Map")
    if not filtered_df.empty:
        # Generate and display map
        m = create_map(filtered_df)
        st_data = st_folium(m, width=900, height=600)
    else:
        st.warning("No sightings match the selected filters. Try adjusting your criteria.")

with col2:
    st.subheader("Sightings Statistics")

    st.markdown("---")
    st.markdown("**Top 10 Countries by Sightings**")
    country_counts = filtered_df['country'].value_counts().head(10)
    if not country_counts.empty:
        fig_country = px.bar(
            country_counts,
            x=country_counts.values,
            y=country_counts.index,
            orientation='h',
            labels={'x': 'Number of Sightings', 'y': 'Country'},
            height=350
        )
        fig_country.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_country, use_container_width=True)
    else:
        st.info("No country data for selected filters.")

    st.markdown("---")
    st.markdown("**Sightings Timeline Trend**")
    # Group by year and count sightings
    yearly_counts = filtered_df['year'].value_counts().sort_index().reset_index()
    yearly_counts.columns = ['Year', 'Count']
    if not yearly_counts.empty:
        fig_timeline = px.line(
            yearly_counts,
            x='Year',
            y='Count',
            labels={'Year': 'Year', 'Count': 'Number of Sightings'},
            title='UFO Sightings Over Time'
        )
        st.plotly_chart(fig_timeline, use_container_width=True)
    else:
        st.info("No timeline data for selected filters.")

    st.markdown("---")
    st.markdown("**Top 10 Sighting Shapes**")
    shape_counts = filtered_df['shape'].value_counts().head(10)
    if not shape_counts.empty:
        fig_shape = px.bar(
            shape_counts,
            x=shape_counts.values,
            y=shape_counts.index,
            orientation='h',
            labels={'x': 'Number of Sightings', 'y': 'Shape'},
            height=350
        )
        fig_shape.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_shape, use_container_width=True)
    else:
        st.info("No shape data for selected filters.")