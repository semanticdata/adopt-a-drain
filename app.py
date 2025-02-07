import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Page config
st.set_page_config(
    page_title="Adopt-a-Drain Dashboard",
    page_icon="🌊",
    layout="wide"
)

# Load and prepare data
@st.cache_data
def load_data():
    # Read CSVs
    adoptions = pd.read_csv('adoptions.csv')
    cleanings = pd.read_csv('cleanings.csv')
    
    # Convert dates
    adoptions['Adoption Date'] = pd.to_datetime(adoptions['Adoption Date'])
    cleanings['Cleaning Date'] = pd.to_datetime(cleanings['Cleaning Date'])
    
    # Convert collected amount to numeric, replacing empty strings with 0
    cleanings['Collected Amount'] = pd.to_numeric(cleanings['Collected Amount'].replace('', '0'))
    
    return adoptions, cleanings

adoptions, cleanings = load_data()

# Add filters in sidebar
st.sidebar.header("Filters")

# Year filter
years = ['All'] + sorted(cleanings['Cleaning Date'].dt.year.unique().tolist(), reverse=True)
selected_year = st.sidebar.selectbox("Select Year", years)

# Filter data based on year if selected
if selected_year != 'All':
    cleanings = cleanings[cleanings['Cleaning Date'].dt.year == selected_year]
    adoptions = adoptions[adoptions['Adoption Date'].dt.year == selected_year]

# Watershed filter
watersheds = ['All'] + sorted(cleanings['Watershed'].unique().tolist())
selected_watershed = st.sidebar.selectbox("Watershed", watersheds)

# Filter data based on watershed if selected
if selected_watershed != 'All':
    cleanings = cleanings[cleanings['Watershed'] == selected_watershed]
    adoptions = adoptions[adoptions['Watershed'] == selected_watershed]

# Title with year if selected
if selected_year != 'All':
    st.title(f"🌊 Adopt-a-Drain Program Dashboard ({selected_year})")
else:
    st.title("🌊 Adopt-a-Drain Program Dashboard")

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Adoptions", len(adoptions))
    
with col2:
    st.metric("Total Cleanings", len(cleanings))
    
with col3:
    total_collected = f"{cleanings['Collected Amount'].sum():,.1f} lbs"
    st.metric("Total Debris Collected", total_collected)
    
with col4:
    avg_per_cleaning = f"{cleanings['Collected Amount'].mean():,.1f} lbs"
    st.metric("Avg. Debris per Cleaning", avg_per_cleaning)

# Two column layout for charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("Cleanings Over Time")
    
    # Monthly cleaning counts
    monthly_cleanings = cleanings.set_index('Cleaning Date').resample('M').size()
    
    fig = px.line(monthly_cleanings, 
                  title="Monthly Cleaning Activity",
                  labels={"value": "Number of Cleanings", "Cleaning Date": "Date"})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Most Common Debris Types")
    
    # Count primary debris types
    debris_counts = cleanings['Primary Debris'].value_counts()
    
    fig = px.pie(values=debris_counts.values, 
                 names=debris_counts.index,
                 title="Primary Debris Distribution")
    st.plotly_chart(fig, use_container_width=True)

# Watershed Analysis
st.subheader("Watershed Activity")

watershed_stats = cleanings.groupby('Watershed').agg({
    'ID': 'count',
    'Collected Amount': 'sum'
}).round(1)

watershed_stats.columns = ['Number of Cleanings', 'Total Debris Collected (lbs)']
st.dataframe(watershed_stats, use_container_width=True)

# Top Volunteers
st.subheader("Top Volunteers")

top_volunteers = cleanings.groupby('User Display Name').agg({
    'ID': 'count',
    'Collected Amount': 'sum'
}).round(1)

top_volunteers.columns = ['Number of Cleanings', 'Total Debris Collected (lbs)']
top_volunteers = top_volunteers.sort_values('Total Debris Collected (lbs)', ascending=False).head(10)
st.dataframe(top_volunteers, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("Data from the Adopt-a-Drain program. Dashboard created with Streamlit.") 