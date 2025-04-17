import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from typing import Tuple

# Page config
st.set_page_config(page_title="Adopt-a-Drain Dashboard", page_icon="🌊", layout="wide")


# Load and prepare data
@st.cache_data(ttl=3600)  # Cache for 1 hour
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    try:
        # Read CSVs with error handling
        adoptions = pd.read_csv("adoptions.csv")
        cleanings = pd.read_csv("cleanings.csv")

        # Convert dates
        adoptions["Adoption Date"] = pd.to_datetime(adoptions["Adoption Date"])
        cleanings["Cleaning Date"] = pd.to_datetime(cleanings["Cleaning Date"])

        # Convert collected amount to numeric, replacing empty strings with 0
        cleanings["Collected Amount"] = pd.to_numeric(
            cleanings["Collected Amount"].replace("", "0")
        )

        return adoptions, cleanings
    except Exception as e:
        st.sidebar.error(f"Error in load_data: {str(e)}")
        raise


# Load data
try:
    adoptions, cleanings = load_data()
except Exception as e:
    st.error(f"Error loading data: {str(e)}")
    st.stop()

# Sidebar filters
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
st.title(
    f"🌊 Adopt-a-Drain Dashboard ({selected_year})"
    if selected_year != "All"
    else "🌊 Adopt-a-Drain Dashboard"
)

# Key Metrics Row
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Adoptions", len(adoptions))

with col2:
    st.metric("Total Cleanings", len(cleanings))

with col3:
    total_collected = f"{cleanings['Collected Amount'].sum():,.1f} lbs"
    st.metric("Total Collected Amount", total_collected)

with col4:
    avg_per_cleaning = f"{cleanings['Collected Amount'].mean():,.1f} lbs"
    st.metric("Avg. Debris per Cleaning", avg_per_cleaning)

# Two column layout for charts
col1, col2 = st.columns(2)


@st.cache_data
def get_monthly_cleanings(cleanings_df: pd.DataFrame) -> pd.Series:
    return cleanings_df.set_index("Cleaning Date").resample("ME").size()


@st.cache_data
def get_monthly_adoptions(adoptions_df: pd.DataFrame) -> pd.Series:
    return adoptions_df.set_index("Adoption Date").resample("ME").size()


with col1:
    # Monthly cleaning counts - using 'ME' instead of deprecated 'M'
    monthly_cleanings = get_monthly_cleanings(cleanings)

    fig = px.line(
        monthly_cleanings,
        title="Monthly Cleaning Activity",
        labels={"value": "Number of Cleanings", "Cleaning Date": "Date"},
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    # Monthly adoption counts
    monthly_adoptions = get_monthly_adoptions(adoptions)

    fig = px.line(
        monthly_adoptions,
        title="Monthly Adoption Activity",
        labels={"value": "Number of Adoptions", "Adoption Date": "Date"},
    )
    st.plotly_chart(fig, use_container_width=True)

# Two column layout for additional charts
col3, col4 = st.columns(2)


@st.cache_data
def get_monthly_collected_amount(cleanings_df: pd.DataFrame) -> pd.Series:
    return (
        cleanings_df.set_index("Cleaning Date")["Collected Amount"].resample("ME").sum()
    )


with col3:
    # Monthly collected amount
    monthly_collected_amount = get_monthly_collected_amount(cleanings)

    fig = px.line(
        monthly_collected_amount,
        title="Monthly Collected Amount",
        labels={"value": "Collected Amount (lbs)", "Cleaning Date": "Date"},
    )
    st.plotly_chart(fig, use_container_width=True)

with col4:
    # Combined adoption and cleaning trends
    monthly_cleanings = get_monthly_cleanings(cleanings)
    monthly_adoptions = get_monthly_adoptions(adoptions)

    combined_df = pd.DataFrame(
        {"Monthly Cleanings": monthly_cleanings, "Monthly Adoptions": monthly_adoptions}
    ).reset_index()

    fig = px.line(
        combined_df,
        x="index",  # Use the index for the x-axis
        y=["Monthly Cleanings", "Monthly Adoptions"],
        title="Adoption and Cleaning Trends",
        labels={"value": "Count", "index": "Date"},
    )
    st.plotly_chart(fig, use_container_width=True)


@st.cache_data
def calculate_yearly_summary(
    adoptions_df: pd.DataFrame, cleanings_df: pd.DataFrame
) -> pd.DataFrame:
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


col5, col6 = st.columns(2)

with col5:
    # Yearly Summary
    try:
        if adoptions.empty or cleanings.empty:
            st.warning("No data available for the selected filters.")
        else:
            yearly_summary = calculate_yearly_summary(adoptions, cleanings)
            if yearly_summary.empty:
                st.warning("No yearly summary data available for the selected filters.")
            else:
                # Bar chart for yearly summary
                fig = px.bar(
                    yearly_summary.reset_index(),
                    x="Year",
                    y=["Adoptions", "Cleanings"],
                    title="Yearly Adoptions and Cleanings Summary",
                    barmode="group",
                    labels={"value": "Count", "Year": "Year"},
                )
                st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error processing yearly summary: {str(e)}")

with col6:
    # Yearly Trends
    try:
        if adoptions.empty or cleanings.empty:
            st.warning("No data available for the selected filters.")
        else:
            yearly_adoptions = (
                adoptions.set_index("Adoption Date").resample("YE").size()
            )
            yearly_cleanings = (
                cleanings.set_index("Cleaning Date").resample("YE").size()
            )

            yearly_trends_df = pd.DataFrame(
                {
                    "Yearly Adoptions": yearly_adoptions,
                    "Yearly Cleanings": yearly_cleanings,
                }
            ).reset_index()

            # Yearly bar graph
            fig_bar = px.bar(
                yearly_trends_df,
                x="index",  # Use the index for the x-axis
                y=["Yearly Adoptions", "Yearly Cleanings"],
                title="Yearly Adoption and Cleaning Counts",
                labels={"value": "Count", "index": "Year"},
                barmode="group",
            )
            st.plotly_chart(fig_bar, use_container_width=True)
    except Exception as e:
        st.error(f"Error processing yearly trends: {str(e)}")

# Primary Debris Distribution
try:
    if cleanings.empty:
        st.warning("No cleaning data available for the selected filters.")
    else:
        debris_counts = cleanings["Primary Debris"].value_counts()

        fig = px.pie(
            values=debris_counts.values,
            names=debris_counts.index,
            title="Debris Distribution",
        )
        st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"Error processing debris data: {str(e)}")


# Map for cleaning locations
st.subheader("Cleaning Locations Map")

try:
    if cleanings.empty:
        st.warning("No cleaning data available for the selected filters.")
    else:
        fig = px.scatter_map(
            cleanings,
            lat="Latitude",
            lon="Longitude",
            hover_name="User Display Name",
            hover_data=["Cleaning Date", "Collected Amount"],
            color_discrete_sequence=["fuchsia"],
            zoom=12,
            height=550,
        )
        fig.update_layout(mapbox_style="open-street-map")
        fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
        st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"Error processing map data: {str(e)}")

# Top Volunteers

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

        # Bar chart for top volunteers
        fig = px.bar(
            top_volunteers.reset_index(),
            x="User Display Name",
            y=["Number of Cleanings", "Total Debris Collected (lbs)"],
            title="Top Volunteers",
            barmode="group",
            labels={
                "value": "Count / Collected Amount (lbs)",
                "User Display Name": "Volunteer",
            },
        )
        st.plotly_chart(fig, use_container_width=True)
except Exception as e:
    st.error(f"Error processing volunteer data: {str(e)}")


# Watershed Analysis

try:
    watershed_stats = (
        cleanings.groupby("Watershed")
        .agg({"ID": "count", "Collected Amount": "sum"})
        .round(1)
        .reset_index()
    )

    if watershed_stats.empty:
        st.warning("No watershed data available for the selected filters.")
    else:
        watershed_stats.columns = [
            "Watershed",
            "Number of Cleanings",
            "Total Debris Collected (lbs)",
        ]

        # Combined bar chart for number of cleanings and collected amount by watershed
        fig = px.bar(
            watershed_stats,
            x="Watershed",
            y=["Number of Cleanings", "Total Debris Collected (lbs)"],
            title="Watershed Specific Cleaning Activity",
            barmode="group",
            labels={
                "value": "Count / Collected Amount (lbs)",
                "Watershed": "Watershed",
            },
        )
        st.plotly_chart(fig, use_container_width=True)

except Exception as e:
    st.error(f"Error processing watershed data: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    "Data sourced from the [Adopt-a-Drain](https://mn.adopt-a-drain.org/) program for Crystal, Minnesota. Dashboard created with [Streamlit](https://streamlit.io/)."
)
