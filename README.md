# Adopt-a-Drain Dashboard

A dashboard for the Adopt-a-Drain program in Crystal, Minnesota, built with Plotly Dash.

## 🚀 Usage

1. Clone the repository:

```bash
git clone https://github.com/semanticdata/adopt-a-drain.git
cd adopt-a-drain
```

2. Create a virtual environment (optional but recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install required packages:

```bash
pip install -r requirements.txt
```

4. Run the dashboard:

```bash
python dashboard.py
```

The dashboard will be available at <http://127.0.0.1:8050/>

## 📊 Features

- **Modern UI**: Clean interface built with Dash and Bootstrap components
- **Filters**: Filter data by year and watershed.
- **Key Metrics**: Display total adoptions, total cleanings, total collected amount, and average debris per cleaning.
- **Monthly Trends**: Line charts showing monthly cleaning and adoption activities.
- **Yearly Summary**: Bar charts summarizing yearly adoptions and cleanings.
- **Yearly Trends**: Bar charts showing yearly adoption and cleaning counts.
- **Debris Distribution**: Pie chart displaying the distribution of primary debris types.
- **Cleaning Locations Map**: Interactive map showing cleaning locations.
- **Top Volunteers**: Bar chart highlighting the top volunteers by number of cleanings and total debris collected.
- **Watershed Activity**: Bar chart showing the number of cleanings and total debris collected by watershed.

## 📜 License

The code in this repository is available under the [MIT License](LICENSE).
