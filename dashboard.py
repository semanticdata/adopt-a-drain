import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# import psutil

# Page config
st.set_page_config(page_title="Adopt-a-Drain Dashboard", page_icon="🌊", layout="wide")


# Load and prepare data
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data():
    try:
        # Print current working directory
        import os

        # st.sidebar.write(f"Current working directory: {os.getcwd()}")

        # Read CSVs with error handling
        try:
            adoptions = pd.read_csv("adoptions.csv")
            # st.sidebar.write("Successfully loaded adoptions.csv")
        except Exception as e:
            st.sidebar.error(f"Error loading adoptions.csv: {str(e)}")
            raise

        try:
            cleanings = pd.read_csv("cleanings.csv")
            # st.sidebar.write("Successfully loaded cleanings.csv")
        except Exception as e:
            st.sidebar.error(f"Error loading cleanings.csv: {str(e)}")
            raise

        # Convert dates
        adoptions["Adoption Date"] = pd.to_datetime(adoptions["Adoption Date"])
        cleanings["Cleaning Date"] = pd.to_datetime(cleanings["Cleaning Date"])

        # Convert collected amount to numeric, replacing empty strings with 0
        cleanings["Collected Amount"] = pd.to_numeric(
            cleanings["Collected Amount"].replace("", "0")
        )

        # Verify data loaded correctly
        # st.sidebar.write(f"Adoptions columns: {adoptions.columns.tolist()}")
        # st.sidebar.write(f"Cleanings columns: {cleanings.columns.tolist()}")

        return adoptions, cleanings
    except Exception as e:
        st.sidebar.error(f"Error in load_data: {str(e)}")
        raise


try:
    adoptions, cleanings = load_data()
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Add after the load_data() call
# st.sidebar.write("Debug Info:")
# st.sidebar.write(f"Number of adoptions: {len(adoptions)}")
# st.sidebar.write(f"Number of cleanings: {len(cleanings)}")
# st.sidebar.write(f"Available watersheds: {cleanings['Watershed'].unique()}")

# Add filters in sidebar
st.sidebar.header("Filters")

# Year filter
years = ["All"] + sorted(
    cleanings["Cleaning Date"].dt.year.unique().tolist(), reverse=True
)
selected_year = st.sidebar.selectbox("Select Year", years)

# Filter data based on year if selected
if selected_year != "All":
    cleanings = cleanings[cleanings["Cleaning Date"].dt.year == selected_year]
    adoptions = adoptions[adoptions["Adoption Date"].dt.year == selected_year]

# Watershed filter
watersheds = ["All"] + sorted(cleanings["Watershed"].unique().tolist())
selected_watershed = st.sidebar.selectbox("Watershed", watersheds)

# Filter data based on watershed if selected
if selected_watershed != "All":
    cleanings = cleanings[cleanings["Watershed"] == selected_watershed]
    adoptions = adoptions[adoptions["Watershed"] == selected_watershed]

# Title with year if selected
if selected_year != "All":
    st.title(f"🌊 Adopt-a-Drain Dashboard ({selected_year})")
else:
    st.title("🌊 Adopt-a-Drain Dashboard")

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


@st.cache_data
def get_monthly_cleanings(cleanings_df):
    return cleanings_df.set_index("Cleaning Date").resample("ME").size()


with col1:
    # st.subheader("Cleanings Over Time")

    # Monthly cleaning counts - using 'ME' instead of deprecated 'M'
    monthly_cleanings = get_monthly_cleanings(cleanings)

    fig = px.line(
        monthly_cleanings,
        title="Monthly Cleaning Activity",
        labels={"value": "Number of Cleanings", "Cleaning Date": "Date"},
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # st.subheader("Most Common Debris Types")

    # Count primary debris types
    debris_counts = cleanings["Primary Debris"].value_counts()

    fig = px.pie(
        values=debris_counts.values,
        names=debris_counts.index,
        title="Primary Debris Distribution",
    )
    st.plotly_chart(fig, use_container_width=True)

# Watershed Analysis
st.subheader("Watershed Activity")

try:
    watershed_stats = (
        cleanings.groupby("Watershed")
        .agg({"ID": "count", "Collected Amount": "sum"})
        .round(1)
    )

    if watershed_stats.empty:
        st.warning("No watershed data available for the selected filters.")
    else:
        watershed_stats.columns = [
            "Number of Cleanings",
            "Total Debris Collected (lbs)",
        ]
        st.dataframe(watershed_stats, use_container_width=True)
except Exception as e:
    st.error(f"Error processing watershed data: {str(e)}")

# Top Volunteers
st.subheader("Top Volunteers")

try:
    if cleanings.empty:
        st.warning("No cleaning data available for the selected filters.")
    else:
        top_volunteers = (
            cleanings.groupby("User Display Name")
            .agg({"ID": "count", "Collected Amount": "sum"})
            .round(1)
        )

        top_volunteers.columns = ["Number of Cleanings", "Total Debris Collected (lbs)"]
        top_volunteers = top_volunteers.sort_values(
            "Total Debris Collected (lbs)", ascending=False
        ).head(10)
        st.dataframe(top_volunteers, use_container_width=True)
except Exception as e:
    st.error(f"Error processing volunteer data: {str(e)}")


@st.cache_data
def calculate_yearly_summary(adoptions_df, cleanings_df):
    # Get unique years from both dataframes
    all_years = sorted(
        pd.concat(
            [
                adoptions_df["Adoption Date"].dt.year,
                cleanings_df["Cleaning Date"].dt.year,
            ]
        ).unique()
    )

    yearly_summary = pd.DataFrame(
        {
            "Year": all_years,
            "Adoptions": adoptions_df["Adoption Date"]
            .dt.year.value_counts()
            .reindex(all_years, fill_value=0),
            "Cleanings": cleanings_df["Cleaning Date"]
            .dt.year.value_counts()
            .reindex(all_years, fill_value=0),
        }
    ).set_index("Year")

    return yearly_summary


# Yearly Summary
st.subheader("Yearly Adoptions and Cleanings Summary")

try:
    if adoptions.empty or cleanings.empty:
        st.warning("No data available for the selected filters.")
    else:
        yearly_summary = calculate_yearly_summary(adoptions, cleanings)
        if yearly_summary.empty:
            st.warning("No yearly summary data available for the selected filters.")
        else:
            st.dataframe(yearly_summary, use_container_width=True)
except Exception as e:
    st.error(f"Error processing yearly summary: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "Data from the [Adopt-a-Drain](https://mn.adopt-a-drain.org/) program. Dashboard created with Streamlit."
)
