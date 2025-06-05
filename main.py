"""
Adopt-a-Drain Dashboard

A Streamlit dashboard for visualizing drain adoption and cleaning data from
the Crystal, Minnesota Adopt-a-Drain program. Provides insights into volunteer
activity, debris collection trends, and geographic distribution of cleanings.

Author: Crystal Adopt-a-Drain Program
Created: 2024
"""

from typing import Tuple

import pandas as pd
import plotly.express as px
import streamlit as st

# ================================
# CONFIGURATION & CONSTANTS
# ================================

# Page configuration
st.set_page_config(page_title="Adopt-a-Drain Dashboard", page_icon="🌊", layout="wide")

# Constants
CACHE_TTL = 3600  # 1 hour cache duration
DEFAULT_ZOOM = 12
TOP_VOLUNTEERS_LIMIT = 10

# ================================
# DATA LOADING & PREPROCESSING
# ================================


@st.cache_data(ttl=CACHE_TTL)
def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Load and preprocess adoption and cleaning data from CSV files.

    Returns:
        Tuple[pd.DataFrame, pd.DataFrame]: A tuple containing:
            - adoptions: DataFrame with adoption records
            - cleanings: DataFrame with cleaning records

    Raises:
        Exception: If there's an error reading CSV files or processing data

    Note:
        Data is cached for 1 hour to improve performance
    """
    try:
        # Read CSV files with error handling
        adoptions = pd.read_csv("adoptions.csv")
        cleanings = pd.read_csv("cleanings.csv")

        # Convert date columns to datetime
        adoptions["Adoption Date"] = pd.to_datetime(adoptions["Adoption Date"])
        cleanings["Cleaning Date"] = pd.to_datetime(cleanings["Cleaning Date"])

        # Clean and convert collected amount to numeric
        # Replace empty strings with 0 for proper numeric conversion
        cleanings["Collected Amount"] = pd.to_numeric(
            cleanings["Collected Amount"].replace("", "0")
        )

        return adoptions, cleanings
    except Exception as e:
        st.sidebar.error(f"Error in load_data: {str(e)}")
        raise


# ================================
# DATA AGGREGATION FUNCTIONS
# ================================


@st.cache_data
def get_monthly_cleanings(cleanings_df: pd.DataFrame) -> pd.Series:
    """
    Aggregate cleaning data by month.

    Args:
        cleanings_df: DataFrame containing cleaning records

    Returns:
        pd.Series: Monthly cleaning counts indexed by date
    """
    return cleanings_df.set_index("Cleaning Date").resample("ME").size()


@st.cache_data
def get_monthly_adoptions(adoptions_df: pd.DataFrame) -> pd.Series:
    """
    Aggregate adoption data by month.

    Args:
        adoptions_df: DataFrame containing adoption records

    Returns:
        pd.Series: Monthly adoption counts indexed by date
    """
    return adoptions_df.set_index("Adoption Date").resample("ME").size()


@st.cache_data
def get_monthly_collected_amount(cleanings_df: pd.DataFrame) -> pd.Series:
    """
    Aggregate debris collection amounts by month.

    Args:
        cleanings_df: DataFrame containing cleaning records

    Returns:
        pd.Series: Monthly collected amounts (in lbs) indexed by date
    """
    return (
        cleanings_df.set_index("Cleaning Date")["Collected Amount"].resample("ME").sum()
    )


@st.cache_data
def calculate_yearly_summary(
    adoptions_df: pd.DataFrame, cleanings_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Calculate yearly summary statistics for adoptions and cleanings.

    Args:
        adoptions_df: DataFrame containing adoption records
        cleanings_df: DataFrame containing cleaning records

    Returns:
        pd.DataFrame: Yearly summary with columns for adoptions and cleanings
    """
    # Extract unique years from both datasets
    all_years = sorted(
        pd.concat(
            [
                adoptions_df["Adoption Date"].dt.year,
                cleanings_df["Cleaning Date"].dt.year,
            ]
        ).unique()
    )

    # Create summary DataFrame with proper indexing
    yearly_summary = pd.DataFrame(
        {
            "Year": all_years,
            "Adoptions": (
                adoptions_df["Adoption Date"]
                .dt.year.value_counts()
                .reindex(all_years, fill_value=0)
            ),
            "Cleanings": (
                cleanings_df["Cleaning Date"]
                .dt.year.value_counts()
                .reindex(all_years, fill_value=0)
            ),
        }
    ).set_index("Year")

    return yearly_summary


# ================================
# MAIN APPLICATION
# ================================


def main():
    """Main application logic for the Adopt-a-Drain dashboard."""

    # Load data with error handling
    try:
        adoptions, cleanings = load_data()
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.stop()

    # ============================
    # SIDEBAR FILTERS
    # ============================

    st.sidebar.header("Filters")

    # Year filter
    years = ["All"] + sorted(
        cleanings["Cleaning Date"].dt.year.unique().tolist(), reverse=True
    )
    selected_year = st.sidebar.selectbox("Select Year", years)

    # Apply year filter
    if selected_year != "All":
        cleanings = cleanings[cleanings["Cleaning Date"].dt.year == selected_year]
        adoptions = adoptions[adoptions["Adoption Date"].dt.year == selected_year]

    # Watershed filter
    watersheds = ["All"] + sorted(cleanings["Watershed"].unique().tolist())
    selected_watershed = st.sidebar.selectbox("Watershed", watersheds)

    # Apply watershed filter
    if selected_watershed != "All":
        cleanings = cleanings[cleanings["Watershed"] == selected_watershed]
        adoptions = adoptions[adoptions["Watershed"] == selected_watershed]

    # ============================
    # DASHBOARD HEADER
    # ============================

    # Dynamic title based on selected year
    title = (
        f"🌊 Adopt-a-Drain Dashboard ({selected_year})"
        if selected_year != "All"
        else "🌊 Adopt-a-Drain Dashboard"
    )
    st.title(title)

    # ============================
    # KEY METRICS
    # ============================

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

    # ============================
    # TREND CHARTS (TOP ROW)
    # ============================

    col1, col2 = st.columns(2)

    with col1:
        # Monthly cleaning activity trend
        monthly_cleanings = get_monthly_cleanings(cleanings)
        fig = px.line(
            monthly_cleanings,
            title="Monthly Cleaning Activity",
            labels={"value": "Number of Cleanings", "Cleaning Date": "Date"},
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # Monthly adoption activity trend
        monthly_adoptions = get_monthly_adoptions(adoptions)
        fig = px.line(
            monthly_adoptions,
            title="Monthly Adoption Activity",
            labels={"value": "Number of Adoptions", "Adoption Date": "Date"},
        )
        st.plotly_chart(fig, use_container_width=True)

    # ============================
    # ADDITIONAL CHARTS (SECOND ROW)
    # ============================

    col3, col4 = st.columns(2)

    with col3:
        # Monthly collected debris amount
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
            {
                "Monthly Cleanings": monthly_cleanings,
                "Monthly Adoptions": monthly_adoptions,
            }
        ).reset_index()

        fig = px.line(
            combined_df,
            x="index",
            y=["Monthly Cleanings", "Monthly Adoptions"],
            title="Adoption and Cleaning Trends",
            labels={"value": "Count", "index": "Date"},
        )
        st.plotly_chart(fig, use_container_width=True)

    # ============================
    # YEARLY ANALYSIS (THIRD ROW)
    # ============================

    col5, col6 = st.columns(2)

    with col5:
        # Yearly summary bar chart
        try:
            if adoptions.empty or cleanings.empty:
                st.warning("No data available for the selected filters.")
            else:
                yearly_summary = calculate_yearly_summary(adoptions, cleanings)
                if yearly_summary.empty:
                    st.warning(
                        "No yearly summary data available for the selected filters."
                    )
                else:
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
        # Yearly trends using YearEnd resampling
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

                fig_bar = px.bar(
                    yearly_trends_df,
                    x="index",
                    y=["Yearly Adoptions", "Yearly Cleanings"],
                    title="Yearly Adoption and Cleaning Counts",
                    labels={"value": "Count", "index": "Year"},
                    barmode="group",
                )
                st.plotly_chart(fig_bar, use_container_width=True)
        except Exception as e:
            st.error(f"Error processing yearly trends: {str(e)}")

    # ============================
    # DEBRIS ANALYSIS
    # ============================

    # Primary debris type distribution
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

    # ============================
    # GEOGRAPHIC VISUALIZATION
    # ============================

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
                zoom=DEFAULT_ZOOM,
                height=550,
            )
            fig.update_layout(mapbox_style="open-street-map")
            fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0})
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Error processing map data: {str(e)}")

    # ============================
    # VOLUNTEER ANALYSIS
    # ============================

    # Top volunteers by debris collected
    try:
        if cleanings.empty:
            st.warning("No cleaning data available for the selected filters.")
        else:
            top_volunteers = (
                cleanings.groupby("User Display Name")
                .agg({"ID": "count", "Collected Amount": "sum"})
                .round(1)
            )

            top_volunteers.columns = [
                "Number of Cleanings",
                "Total Debris Collected (lbs)",
            ]
            top_volunteers = top_volunteers.sort_values(
                "Total Debris Collected (lbs)", ascending=False
            ).head(TOP_VOLUNTEERS_LIMIT)

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

    # ============================
    # WATERSHED ANALYSIS
    # ============================

    # Watershed-specific cleaning activity
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

    # ============================
    # FOOTER
    # ============================

    st.markdown("---")
    st.markdown(
        "Data sourced from the [Adopt-a-Drain](https://mn.adopt-a-drain.org/) "
        "program for Crystal, Minnesota. Dashboard created with "
        "[Streamlit](https://streamlit.io/)."
    )


# ================================
# APPLICATION ENTRY POINT
# ================================

if __name__ == "__main__":
    main()
