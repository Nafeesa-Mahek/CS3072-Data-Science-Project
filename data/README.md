# Data

Our project uses **three free, public sources**. None of the data comes from Kaggle.
The main dataset is NYC taxi trips. The other two add weather and the congestion-toll zone to each trip.

![How the data sources fit together](data_sources.png)

## Files in this folder

| File | What it is | Rows |
|---|---|---|
| `trips_sample.csv.gz` | **Main dataset.** NYC yellow taxi trips, Oct 2024 – Sep 2025, 80,000 sampled per month (compressed CSV) | 960,000 |
| `taxi_zone_lookup.csv` | Taxi zone ID → zone name and borough | 265 |
| `weather_hourly_nyc.csv` | Hourly NYC weather: temperature, rain, snow, wind | ≈ 8,760 |
| `cbd_taxi_zones.csv` | Taxi zones inside the congestion pricing (toll) zone | small |
| `00_load_data.ipynb` | The notebook that created the 4 data files from the official sources | – |
| `data_sources.png` | The diagram above | – |
| `README.md` | This file | – |

## How to use the data

1. **Download the 4 data files** from this folder to your computer: click a file, then the download button (↓) at the top right.
2. **Put them in the same folder as your notebook.** In Google Colab, click the 📁 folder icon on the left and drag the 4 files in. Colab deletes uploaded files when the session ends, so upload them again each time you open a notebook.
3. **Load them** by pasting this in your first cell:

```python
import pandas as pd

trips = pd.read_csv("trips_sample.csv.gz",
                    parse_dates=["tpep_pickup_datetime", "tpep_dropoff_datetime"])
zones = pd.read_csv("taxi_zone_lookup.csv")
weather = pd.read_csv("weather_hourly_nyc.csv", parse_dates=["time"])
cbd = pd.read_csv("cbd_taxi_zones.csv")
```

`trips_sample.csv.gz` is compressed so it fits on GitHub. pandas opens it like a normal CSV, so don't unzip it.

**Don't edit these files or re-run `00_load_data.ipynb`.** Everyone must use exactly the same data so our results match.

## The sources

### 1. NYC TLC Trip Record Data: Yellow Taxi Trip Records (main dataset)

- **Provider:** NYC Taxi & Limousine Commission (official city data)
- **Page:** https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
- **Column meanings:** https://www.nyc.gov/assets/tlc/downloads/pdf/data_dictionary_trip_records_yellow.pdf
- **Zone lookup:** https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv
- **Why these months:** they cover 3 months before and 9 months after congestion pricing began on 5 January 2025.

| Column | Meaning |
|---|---|
| `tpep_pickup_datetime` | Pickup date and time |
| `tpep_dropoff_datetime` | Drop-off date and time (only used to calculate trip duration, our outcome) |
| `passenger_count` | Number of passengers |
| `trip_distance` | Trip distance in miles |
| `RatecodeID` | Rate type (for example 2 = JFK airport flat rate) |
| `PULocationID` | Pickup taxi zone ID |
| `DOLocationID` | Drop-off taxi zone ID |

We left out fare, tip, tolls, fees and total amount on purpose. They are calculated from the trip itself, so using them would leak the answer.

### 2. Open-Meteo Historical Weather

- **Page:** https://open-meteo.com/en/docs/historical-weather-api
- **What we took:** hourly weather for New York City, New York local time, Oct 2024 – Sep 2025
- **Columns:** `time`, `temperature_c`, `precipitation_mm`, `snowfall_cm`, `wind_speed_kmh`
- **Licence:** CC BY 4.0. Credit Open-Meteo in the report.

### 3. MTA Central Business District Taxi Zones

- **Page:** https://catalog-beta.data.gov/dataset/mta-central-business-district-taxi-zones
- **What we use:** the zone ID column, to mark trips that start or end inside the toll zone.

## How to cite the data in the report

1. NYC Taxi and Limousine Commission, "TLC Trip Record Data: Yellow Taxi Trip Records," Oct. 2024 – Sep. 2025. [Online]. Available: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
2. Open-Meteo, "Historical Weather API," CC BY 4.0. [Online]. Available: https://open-meteo.com/en/docs/historical-weather-api
3. Metropolitan Transportation Authority, "MTA Central Business District Taxi Zones," data.ny.gov, 2024. [Online]. Available: https://catalog-beta.data.gov/dataset/mta-central-business-district-taxi-zones
