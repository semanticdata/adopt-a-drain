from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from datetime import datetime
from typing import Tuple

# Initialize the Dash app with a modern theme
app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])


def load_data() -> Tuple[pd.DataFrame, pd.DataFrame]:
    try:
        adoptions = pd.read_csv("adoptions.csv")
        cleanings = pd.read_csv("cleanings.csv")

        adoptions["Adoption Date"] = pd.to_datetime(adoptions["Adoption Date"])
        cleanings["Cleaning Date"] = pd.to_datetime(cleanings["Cleaning Date"])
        cleanings["Collected Amount"] = pd.to_numeric(
            cleanings["Collected Amount"].replace("", "0")
        )

        return adoptions, cleanings
    except Exception as e:
        print(f"Error loading data: {str(e)}")
        raise


# Load data
adoptions, cleanings = load_data()

# Get filter options
years = ["All"] + sorted(
    cleanings["Cleaning Date"].dt.year.unique().tolist(), reverse=True
)
watersheds = ["All"] + sorted(cleanings["Watershed"].unique().tolist())

# Layout
app.layout = dbc.Container(
    [
        # Header with gradient background
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(
                            [
                                html.H1(
                                    "🌊 Adopt-a-Drain Dashboard",
                                    className="display-4 text-white",
                                ),
                                html.P(
                                    "Crystal, Minnesota Drain Adoption Program",
                                    className="lead text-white",
                                ),
                            ],
                            className="p-4 bg-primary rounded-3",
                        )
                    ],
                    width=12,
                )
            ],
            className="mb-4",
        ),
        # Filters with better styling
        dbc.Row(
            [
                dbc.Col(
                    [
                        dbc.Card(
                            [
                                dbc.CardBody(
                                    [
                                        html.H4(
                                            "Dashboard Filters", className="card-title"
                                        ),
                                        html.P(
                                            "Select time period and watershed:",
                                            className="text-muted",
                                        ),
                                        dbc.Label("Year"),
                                        dcc.Dropdown(
                                            id="year-filter",
                                            options=[
                                                {"label": str(y), "value": y}
                                                for y in years
                                            ],
                                            value="All",
                                            className="mb-3",
                                        ),
                                        dbc.Label("Watershed"),
                                        dcc.Dropdown(
                                            id="watershed-filter",
                                            options=[
                                                {"label": w, "value": w}
                                                for w in watersheds
                                            ],
                                            value="All",
                                        ),
                                    ]
                                )
                            ],
                            className="shadow-sm",
                        )
                    ],
                    width=3,
                )
            ],
            className="mb-4",
        ),
        # Key Metrics with improved cards
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H3(
                                        id="total-adoptions",
                                        className="text-primary mb-0",
                                    ),
                                    html.P(
                                        "Total Adoptions", className="text-muted small"
                                    ),
                                ]
                            )
                        ],
                        className="shadow-sm text-center",
                    ),
                    width=3,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H3(
                                        id="total-cleanings",
                                        className="text-success mb-0",
                                    ),
                                    html.P(
                                        "Total Cleanings", className="text-muted small"
                                    ),
                                ]
                            )
                        ],
                        className="shadow-sm text-center",
                    ),
                    width=3,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H3(
                                        id="total-collected", className="text-info mb-0"
                                    ),
                                    html.P(
                                        "Total Collected", className="text-muted small"
                                    ),
                                ]
                            )
                        ],
                        className="shadow-sm text-center",
                    ),
                    width=3,
                ),
                dbc.Col(
                    dbc.Card(
                        [
                            dbc.CardBody(
                                [
                                    html.H3(
                                        id="avg-per-cleaning",
                                        className="text-warning mb-0",
                                    ),
                                    html.P(
                                        "Average per Cleaning",
                                        className="text-muted small",
                                    ),
                                ]
                            )
                        ],
                        className="shadow-sm text-center",
                    ),
                    width=3,
                ),
            ],
            className="mb-4",
        ),
        # Charts with cards
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [dbc.CardBody([dcc.Graph(id="monthly-cleanings")])],
                        className="shadow-sm",
                    ),
                    width=6,
                ),
                dbc.Col(
                    dbc.Card(
                        [dbc.CardBody([dcc.Graph(id="monthly-adoptions")])],
                        className="shadow-sm",
                    ),
                    width=6,
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [dbc.CardBody([dcc.Graph(id="monthly-collected")])],
                        className="shadow-sm",
                    ),
                    width=6,
                ),
                dbc.Col(
                    dbc.Card(
                        [dbc.CardBody([dcc.Graph(id="adoption-cleaning-trends")])],
                        className="shadow-sm",
                    ),
                    width=6,
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [dbc.CardBody([dcc.Graph(id="yearly-summary")])],
                        className="shadow-sm",
                    ),
                    width=6,
                ),
                dbc.Col(
                    dbc.Card(
                        [dbc.CardBody([dcc.Graph(id="yearly-trends")])],
                        className="shadow-sm",
                    ),
                    width=6,
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [dbc.CardBody([dcc.Graph(id="debris-distribution")])],
                        className="shadow-sm",
                    ),
                    width=12,
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [dbc.CardBody([dcc.Graph(id="cleaning-locations-map")])],
                        className="shadow-sm",
                    ),
                    width=12,
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [dbc.CardBody([dcc.Graph(id="top-volunteers")])],
                        className="shadow-sm",
                    ),
                    width=12,
                ),
            ],
            className="mb-4",
        ),
        dbc.Row(
            [
                dbc.Col(
                    dbc.Card(
                        [dbc.CardBody([dcc.Graph(id="watershed-analysis")])],
                        className="shadow-sm",
                    ),
                    width=12,
                ),
            ],
            className="mb-4",
        ),
        # Footer with better styling
        html.Footer(
            [
                html.Hr(),
                html.P(
                    [
                        "Data sourced from the ",
                        html.A(
                            "Adopt-a-Drain",
                            href="https://mn.adopt-a-drain.org/",
                            className="text-primary",
                        ),
                        " program for Crystal, Minnesota. Dashboard created with ",
                        html.A(
                            "Dash",
                            href="https://dash.plotly.com/",
                            className="text-primary",
                        ),
                        ".",
                    ],
                    className="text-center text-muted",
                ),
            ],
            className="mt-4",
        ),
    ],
    fluid=True,
    className="px-4 py-3",
)


# Update the metrics callback to return styled numbers
@callback(
    [
        Output("total-adoptions", "children"),
        Output("total-cleanings", "children"),
        Output("total-collected", "children"),
        Output("avg-per-cleaning", "children"),
    ],
    [Input("year-filter", "value"), Input("watershed-filter", "value")],
)
def update_metrics(selected_year, selected_watershed):
    filtered_adoptions = adoptions.copy()
    filtered_cleanings = cleanings.copy()

    if selected_year != "All":
        filtered_adoptions = filtered_adoptions[
            filtered_adoptions["Adoption Date"].dt.year == selected_year
        ]
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Cleaning Date"].dt.year == selected_year
        ]

    if selected_watershed != "All":
        filtered_adoptions = filtered_adoptions[
            filtered_adoptions["Watershed"] == selected_watershed
        ]
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Watershed"] == selected_watershed
        ]

    return [
        f"{len(filtered_adoptions):,}",
        f"{len(filtered_cleanings):,}",
        f"{filtered_cleanings['Collected Amount'].sum():,.1f} lbs",
        f"{filtered_cleanings['Collected Amount'].mean():,.1f} lbs",
    ]


# Callbacks for graphs
@callback(
    Output("monthly-cleanings", "figure"),
    [Input("year-filter", "value"), Input("watershed-filter", "value")],
)
def update_monthly_cleanings(selected_year, selected_watershed):
    filtered_cleanings = cleanings.copy()
    if selected_year != "All":
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Cleaning Date"].dt.year == selected_year
        ]
    if selected_watershed != "All":
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Watershed"] == selected_watershed
        ]

    monthly_cleanings = (
        filtered_cleanings.set_index("Cleaning Date").resample("ME").size()
    )
    fig = px.line(
        monthly_cleanings,
        title="Monthly Cleaning Activity",
        labels={"value": "Number of Cleanings", "Cleaning Date": "Date"},
    )
    return fig


@callback(
    Output("monthly-adoptions", "figure"),
    [Input("year-filter", "value"), Input("watershed-filter", "value")],
)
def update_monthly_adoptions(selected_year, selected_watershed):
    filtered_adoptions = adoptions.copy()
    if selected_year != "All":
        filtered_adoptions = filtered_adoptions[
            filtered_adoptions["Adoption Date"].dt.year == selected_year
        ]
    if selected_watershed != "All":
        filtered_adoptions = filtered_adoptions[
            filtered_adoptions["Watershed"] == selected_watershed
        ]

    monthly_adoptions = (
        filtered_adoptions.set_index("Adoption Date").resample("ME").size()
    )
    fig = px.line(
        monthly_adoptions,
        title="Monthly Adoption Activity",
        labels={"value": "Number of Adoptions", "Adoption Date": "Date"},
    )
    return fig


@callback(
    Output("monthly-collected", "figure"),
    [Input("year-filter", "value"), Input("watershed-filter", "value")],
)
def update_monthly_collected(selected_year, selected_watershed):
    filtered_cleanings = cleanings.copy()
    if selected_year != "All":
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Cleaning Date"].dt.year == selected_year
        ]
    if selected_watershed != "All":
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Watershed"] == selected_watershed
        ]

    monthly_collected = (
        filtered_cleanings.set_index("Cleaning Date")["Collected Amount"]
        .resample("ME")
        .sum()
    )
    fig = px.line(
        monthly_collected,
        title="Monthly Collected Amount",
        labels={"value": "Collected Amount (lbs)", "Cleaning Date": "Date"},
    )
    return fig


@callback(
    Output("debris-distribution", "figure"),
    [Input("year-filter", "value"), Input("watershed-filter", "value")],
)
def update_debris_distribution(selected_year, selected_watershed):
    filtered_cleanings = cleanings.copy()
    if selected_year != "All":
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Cleaning Date"].dt.year == selected_year
        ]
    if selected_watershed != "All":
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Watershed"] == selected_watershed
        ]

    debris_counts = filtered_cleanings["Primary Debris"].value_counts()
    fig = px.pie(
        values=debris_counts.values,
        names=debris_counts.index,
        title="Debris Distribution",
    )
    return fig


@callback(
    Output("cleaning-locations-map", "figure"),
    [Input("year-filter", "value"), Input("watershed-filter", "value")],
)
def update_map(selected_year, selected_watershed):
    filtered_cleanings = cleanings.copy()
    if selected_year != "All":
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Cleaning Date"].dt.year == selected_year
        ]
    if selected_watershed != "All":
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Watershed"] == selected_watershed
        ]

    fig = px.scatter_map(
        filtered_cleanings,
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
    return fig


@callback(
    Output("top-volunteers", "figure"),
    [Input("year-filter", "value"), Input("watershed-filter", "value")],
)
def update_top_volunteers(selected_year, selected_watershed):
    filtered_cleanings = cleanings.copy()
    if selected_year != "All":
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Cleaning Date"].dt.year == selected_year
        ]
    if selected_watershed != "All":
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Watershed"] == selected_watershed
        ]

    top_volunteers = (
        filtered_cleanings.groupby("User Display Name")
        .agg({"ID": "count", "Collected Amount": "sum"})
        .round(1)
    )
    top_volunteers.columns = ["Number of Cleanings", "Total Debris Collected (lbs)"]
    top_volunteers = top_volunteers.sort_values(
        "Total Debris Collected (lbs)", ascending=False
    ).head(10)

    fig = px.bar(
        top_volunteers.reset_index(),
        x="User Display Name",
        y=["Number of Cleanings", "Total Debris Collected (lbs)"],
        title="Top Volunteers",
        barmode="group",
    )
    return fig


@callback(
    Output("adoption-cleaning-trends", "figure"),
    [Input("year-filter", "value"), Input("watershed-filter", "value")],
)
def update_adoption_cleaning_trends(selected_year, selected_watershed):
    filtered_adoptions = adoptions.copy()
    filtered_cleanings = cleanings.copy()

    if selected_year != "All":
        filtered_adoptions = filtered_adoptions[
            filtered_adoptions["Adoption Date"].dt.year == selected_year
        ]
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Cleaning Date"].dt.year == selected_year
        ]
    if selected_watershed != "All":
        filtered_adoptions = filtered_adoptions[
            filtered_adoptions["Watershed"] == selected_watershed
        ]
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Watershed"] == selected_watershed
        ]

    monthly_cleanings = (
        filtered_cleanings.set_index("Cleaning Date").resample("ME").size()
    )
    monthly_adoptions = (
        filtered_adoptions.set_index("Adoption Date").resample("ME").size()
    )

    combined_df = pd.DataFrame(
        {"Monthly Cleanings": monthly_cleanings, "Monthly Adoptions": monthly_adoptions}
    ).reset_index()

    fig = px.line(
        combined_df,
        x="index",
        y=["Monthly Cleanings", "Monthly Adoptions"],
        title="Adoption and Cleaning Trends",
        labels={"value": "Count", "index": "Date"},
    )
    return fig


@callback(
    Output("yearly-summary", "figure"),
    [Input("year-filter", "value"), Input("watershed-filter", "value")],
)
def update_yearly_summary(selected_year, selected_watershed):
    filtered_adoptions = adoptions.copy()
    filtered_cleanings = cleanings.copy()

    if selected_year != "All":
        filtered_adoptions = filtered_adoptions[
            filtered_adoptions["Adoption Date"].dt.year == selected_year
        ]
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Cleaning Date"].dt.year == selected_year
        ]
    if selected_watershed != "All":
        filtered_adoptions = filtered_adoptions[
            filtered_adoptions["Watershed"] == selected_watershed
        ]
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Watershed"] == selected_watershed
        ]

    # Get unique years from both dataframes
    all_years = sorted(
        pd.concat(
            [
                filtered_adoptions["Adoption Date"].dt.year,
                filtered_cleanings["Cleaning Date"].dt.year,
            ]
        ).unique()
    )

    yearly_summary = pd.DataFrame(
        {
            "Year": all_years,
            "Adoptions": filtered_adoptions["Adoption Date"]
            .dt.year.value_counts()
            .reindex(all_years, fill_value=0),
            "Cleanings": filtered_cleanings["Cleaning Date"]
            .dt.year.value_counts()
            .reindex(all_years, fill_value=0),
        }
    )

    fig = px.bar(
        yearly_summary,
        x="Year",
        y=["Adoptions", "Cleanings"],
        title="Yearly Adoptions and Cleanings Summary",
        barmode="group",
    )
    return fig


@callback(
    Output("yearly-trends", "figure"),
    [Input("year-filter", "value"), Input("watershed-filter", "value")],
)
def update_yearly_trends(selected_year, selected_watershed):
    filtered_adoptions = adoptions.copy()
    filtered_cleanings = cleanings.copy()

    if selected_year != "All":
        filtered_adoptions = filtered_adoptions[
            filtered_adoptions["Adoption Date"].dt.year == selected_year
        ]
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Cleaning Date"].dt.year == selected_year
        ]
    if selected_watershed != "All":
        filtered_adoptions = filtered_adoptions[
            filtered_adoptions["Watershed"] == selected_watershed
        ]
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Watershed"] == selected_watershed
        ]

    yearly_adoptions = (
        filtered_adoptions.set_index("Adoption Date").resample("YE").size()
    )
    yearly_cleanings = (
        filtered_cleanings.set_index("Cleaning Date").resample("YE").size()
    )

    yearly_trends_df = pd.DataFrame(
        {"Yearly Adoptions": yearly_adoptions, "Yearly Cleanings": yearly_cleanings}
    ).reset_index()

    fig = px.bar(
        yearly_trends_df,
        x="index",
        y=["Yearly Adoptions", "Yearly Cleanings"],
        title="Yearly Adoption and Cleaning Counts",
        barmode="group",
        labels={"value": "Count", "index": "Year"},
    )
    return fig


@callback(
    Output("watershed-analysis", "figure"),
    [Input("year-filter", "value"), Input("watershed-filter", "value")],
)
def update_watershed_analysis(selected_year, selected_watershed):
    filtered_cleanings = cleanings.copy()

    if selected_year != "All":
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Cleaning Date"].dt.year == selected_year
        ]
    if selected_watershed != "All":
        filtered_cleanings = filtered_cleanings[
            filtered_cleanings["Watershed"] == selected_watershed
        ]

    watershed_stats = (
        filtered_cleanings.groupby("Watershed")
        .agg({"ID": "count", "Collected Amount": "sum"})
        .round(1)
        .reset_index()
    )

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
    )
    return fig


if __name__ == "__main__":
    app.run(debug=True)
