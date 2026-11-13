"""
Data loading for the CS3072 project:
"The Hidden Cost of Unreliable Travel: Predicting Worst-Case Trip Times
and Evaluating Congestion Pricing".

Everyone on the team loads data through these functions, so we all work
with exactly the same rows.

Use in Google Colab:
    !git clone https://github.com/<github-username>/<repo-name>.git
    %cd <repo-name>
    from data.load_data import load_all
    data = load_all()
    trips, zones, weather, cbd_zone_ids = (data["trips"], data["zones"],
                                           data["weather"], data["cbd_zone_ids"])

The first call downloads from the official sources and saves small copies in
this data/ folder. Later calls read those saved copies, so they are fast.
"""

from pathlib import Path

import pandas as pd

DATA_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Sources (all free and public; none from Kaggle)
# ---------------------------------------------------------------------------
# 1. NYC Taxi & Limousine Commission (TLC) Trip Record Data, yellow taxis
TRIPS_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{}.parquet"
ZONES_URL = "https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
# 2. Open-Meteo historical hourly weather for New York City
WEATHER_URL = (
    "https://archive-api.open-meteo.com/v1/archive"
    "?latitude=40.7128&longitude=-74.0060"
    "&start_date=2024-10-01&end_date=2025-09-30"
    "&hourly=temperature_2m,precipitation,snowfall,wind_speed_10m"
    "&timezone=America%2FNew_York&format=csv"
)
# 3. MTA Central Business District (congestion pricing zone) taxi zones
CBD_URL = "https://data.ny.gov/api/views/yfdc-w5jh/rows.csv?accessType=DOWNLOAD"

# ---------------------------------------------------------------------------
# Sampling settings (do not change without telling the team)
# ---------------------------------------------------------------------------
START_MONTH, END_MONTH = "2024-10", "2025-09"   # 12 months around congestion pricing
N_PER_MONTH = 80_000                             # ~960,000 trips in total
SEED = 42

# Only columns known BEFORE a trip starts (plus drop-off time to build the outcome).
# Fare, tip, tolls, fees and total amount are left out on purpose: they are
# calculated from the trip itself and would leak the answer.
TRIP_COLS = [
    "tpep_pickup_datetime", "tpep_dropoff_datetime", "passenger_count",
    "trip_distance", "RatecodeID", "PULocationID", "DOLocationID",
]

# Saved copies inside data/
TRIPS_FILE = DATA_DIR / "trips_sample.csv.gz"     # compressed CSV, fits GitHub's limit
ZONES_FILE = DATA_DIR / "taxi_zone_lookup.csv"
WEATHER_FILE = DATA_DIR / "weather_hourly_nyc.csv"
CBD_FILE = DATA_DIR / "cbd_taxi_zones.csv"


def build_trip_sample():
    """Download the 12 monthly TLC files and keep a random sample from each."""
    samples = []
    for month in pd.period_range(START_MONTH, END_MONTH, freq="M"):
        df = pd.read_parquet(TRIPS_URL.format(month.strftime("%Y-%m")), columns=TRIP_COLS)
        # Files contain a few trips dated outside their month; keep the right ones only.
        df = df[df["tpep_pickup_datetime"].dt.to_period("M") == month]
        samples.append(df.sample(n=min(N_PER_MONTH, len(df)), random_state=SEED))
        print(f"{month}: {len(df):,} trips in file, {len(samples[-1]):,} sampled")
    trips = pd.concat(samples, ignore_index=True)
    trips.to_csv(TRIPS_FILE, index=False, compression="gzip")
    print(f"Saved {len(trips):,} trips to {TRIPS_FILE.name}")
    return trips


def load_trips(rebuild=False):
    """Trip sample (one row per taxi trip). Downloads only the first time."""
    if TRIPS_FILE.exists() and not rebuild:
        return pd.read_csv(
            TRIPS_FILE,
            parse_dates=["tpep_pickup_datetime", "tpep_dropoff_datetime"],
        )
    return build_trip_sample()


def load_zones():
    """Taxi zone lookup: LocationID -> Borough, Zone, service_zone."""
    if not ZONES_FILE.exists():
        pd.read_csv(ZONES_URL).to_csv(ZONES_FILE, index=False)
    return pd.read_csv(ZONES_FILE)


def load_weather():
    """Hourly NYC weather with columns: time, temperature_c, precipitation_mm,
    snowfall_cm, wind_speed_kmh. Times are New York local time."""
    if not WEATHER_FILE.exists():
        # The Open-Meteo CSV starts with 3 lines of location info before the data.
        raw = pd.read_csv(WEATHER_URL, skiprows=3)
        raw.columns = ["time", "temperature_c", "precipitation_mm",
                       "snowfall_cm", "wind_speed_kmh"]
        raw.to_csv(WEATHER_FILE, index=False)
    return pd.read_csv(WEATHER_FILE, parse_dates=["time"])


def load_cbd_zone_ids():
    """Set of taxi zone IDs inside the congestion pricing zone."""
    if not CBD_FILE.exists():
        pd.read_csv(CBD_URL).to_csv(CBD_FILE, index=False)
    cbd = pd.read_csv(CBD_FILE)
    # Find the zone ID column without relying on its exact name.
    id_cols = [c for c in cbd.columns
               if "location" in c.lower() and "id" in c.lower()]
    if not id_cols:
        raise ValueError(f"No zone ID column found. Columns are: {list(cbd.columns)}")
    return set(cbd[id_cols[0]].astype(int))


def load_all(rebuild=False):
    """Load every dataset the project uses and print a short summary."""
    data = {
        "trips": load_trips(rebuild=rebuild),
        "zones": load_zones(),
        "weather": load_weather(),
        "cbd_zone_ids": load_cbd_zone_ids(),
    }
    print(f"trips:        {data['trips'].shape[0]:,} rows")
    print(f"zones:        {data['zones'].shape[0]:,} rows")
    print(f"weather:      {data['weather'].shape[0]:,} hourly rows")
    print(f"cbd_zone_ids: {len(data['cbd_zone_ids'])} zones in the toll area")
    return data
