# Weather Data Pipeline (dbt + Snowflake)

## Project Overview
This dbt project transforms raw weather data from a single source table in Snowflake (`PALMA.PALMA`) into clean, analytics-ready models for reporting and advanced analysis. The pipeline handles both current and forecasted weather data, including robust handling of missing values and rich model documentation.

---

## Features
- **Source:** Single Snowflake table (`PALMA.PALMA`) containing current and forecast weather data in JSON and structured columns.
- **Staging Models:**
  - `stg_weather_current`: Extracts and cleans current weather metrics.
  - `stg_weather_forecast_daily`: Unpacks and interpolates daily forecast data, filling missing values with neighbor averages or defaults.
  - `stg_weather_forecast_hourly`: Unpacks and cleans hourly forecast data.
- **Mart Models:**
  - `weather_daily_summary`: Aggregates daily metrics (averages, extremes, weather conditions).
  - `weather_current_metrics`: Incremental table of current weather observations.
  - `weather_daily_snapshot`: Combines daily summary with latest current metrics for each day.
  - `weather_trends`: Shows day-to-day changes in key weather metrics.
  - `weather_extremes`: Highlights hottest, coldest, wettest, and highest UV days.
- **Full column-level documentation** for all models.
- **Robust not_null and uniqueness tests** for key columns.
- **Environment variable support** for all Snowflake credentials.

---

## Project Structure
```
models/
  staging/
    stg_weather_current.sql
    stg_weather_forecast_daily.sql
    stg_weather_forecast_hourly.sql
    schema.yml
  marts/
    weather_daily_summary.sql
    weather_current_metrics.sql
    weather_daily_snapshot.sql
    weather_trends.sql
    weather_extremes.sql
    schema.yml
  sources.yml
README.md
.env
profiles.yml
```

---

## Setup & Prerequisites
- Python 3.10 or 3.11 (dbt 1.9.x is not compatible with Python 3.12+)
- dbt-snowflake >= 1.9.4
- Access to a Snowflake account with read/write permissions to the target database/schema

### Environment Variables
Create a `.env` file in your project root with the following variables:
```
SNOWFLAKE_ACCOUNT=your_account
SNOWFLAKE_USER=your_user
SNOWFLAKE_PASSWORD=your_password
SNOWFLAKE_ROLE=your_role
SNOWFLAKE_DATABASE=WEATHER
SNOWFLAKE_WAREHOUSE=your_warehouse
SNOWFLAKE_SCHEMA=PALMA
```

---

## How to Run
1. **Create and activate a compatible Python environment:**
   ```sh
   conda create -n dbt310 python=3.10
   conda activate dbt310
   pip install dbt-snowflake==1.9.4 python-dotenv
   ```
2. **Load environment variables:**
   ```sh
   export $(grep -v '^#' .env | xargs)
   ```
3. **Test your connection:**
   ```sh
   dbt debug
   ```
4. **Build the project:**
   ```sh
   dbt build
   ```
5. **Generate and explore documentation:**
   ```sh
   dbt docs generate
   dbt docs serve
   # Open the provided URL in your browser
   ```

---

## Data Flow
1. **Raw data** ingested into `PALMA.PALMA` (Snowflake).
2. **Staging models** parse, clean, and interpolate missing values.
3. **Mart models** aggregate, combine, and expose analytics-ready tables/views for BI or data science.

---

## Model Details
- **See the dbt docs site** (`dbt docs serve`) for full lineage, model, and column documentation.
- All models are tested for not_null and uniqueness where appropriate.
- Missing forecast values are interpolated using the average of neighboring days, or defaulted to 0 if no neighbors exist.

---

## Troubleshooting
- If you see a `TypeError: Emitter.__init__() got an unexpected keyword argument 'buffer_size'`, you are using an unsupported Python version. Use Python 3.10 or 3.11.
- Ensure all required environment variables are set before running dbt.
- For Snowflake authentication errors, double-check your `.env` and `profiles.yml`.

---

## Extending the Project
- Add new marts or staging models for additional analytics.
- Add or refine tests in the `schema.yml` files.
- Enhance model logic to support new data sources or business rules.

---

## Contact
For questions or improvements, reach out to the project owner or open an issue in your repository.
