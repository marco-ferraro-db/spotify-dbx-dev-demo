# Spotify Databricks Development Demo

This project uses Databricks Asset Bundles to automate the loading of Spotify Charts data from Kaggle and transform it through a medallion architecture using Delta Live Tables.

## Project Structure

```
spotify-dbx-dev-demo/
├── databricks.yml                # Main bundle configuration
├── resources/
│   ├── jobs.yml                 # Job definitions
│   ├── pipelines.yml            # DLT pipeline configuration
│   └── apps.yml                 # App definitions
├── src/
│   ├── setup_catalog.py         # Creates catalog and schemas
│   ├── load_spotify_data.py     # Downloads and loads Spotify data (Bronze)
│   └── dlt_spotify_gold.sql     # DLT pipeline for Silver/Gold layers
├── apps/
│   └── spotify_dashboard/
│       ├── app.py               # Streamlit dashboard application
│       ├── app.yaml             # App configuration
│       └── requirements.txt     # App dependencies
└── README.md
```

## Prerequisites

1. **Databricks CLI** - Install the Databricks CLI:
   ```bash
   pip install databricks-cli
   ```

2. **Authentication** - Configure authentication to your Databricks workspace:
   ```bash
   databricks configure --token
   ```
   - Host: `https://dbc-df2be2c9-07c1.cloud.databricks.com`
   - Token: Your personal access token

3. **Kaggle Credentials** - The job requires Kaggle API credentials. You'll need to:
   - Create a Kaggle account and generate an API token
   - Set up Kaggle credentials in your Databricks workspace as secrets

## What This Bundle Does

### Data Pipeline Architecture (Medallion)

```
Bronze Layer              Silver Layer               Gold Layer
─────────────            ──────────────             ───────────────────
main_schema              prod_schema                prod_schema
├─ spotify_charts   →    ├─ spotify_charts_silver → ├─ spotify_charts_gold
   (raw data)               (cleaned)                  (aggregated)
                                                    └─ top_artists_by_region
```

### Components

1. **Creates Catalog & Schemas**: 
   - Catalog: `spotify_dev`
   - Schema: `main_schema` (bronze layer)
   - Schema: `prod_schema` (silver/gold layers)

2. **Bronze Layer (Job)**: 
   - Downloads Spotify Charts dataset from Kaggle
   - Creates raw table: `spotify_dev.main_schema.spotify_charts`

3. **Silver/Gold Layers (DLT Pipeline)**:
   - Cleans and transforms data (formats dates, drops unnecessary columns)
   - Validates data quality (no nulls in critical fields)
   - Creates aggregated metrics by artist and region
   - Tables: `spotify_charts_silver`, `spotify_charts_gold`, `top_artists_by_region`

## Deployment

### Deploy the Bundle

```bash
# Validate the bundle configuration
databricks bundle validate

# Deploy to the dev target
databricks bundle deploy -t dev
```

### Run the Data Loader Job (Bronze Layer)

```bash
# Run the job to load raw data
databricks bundle run spotify_data_loader -t dev
```

### Run the DLT Pipeline (Silver/Gold Layers)

After the data loader job completes:

```bash
# Start the DLT pipeline
databricks pipelines start spotify_dlt_pipeline
```

Or run from the Databricks UI:
1. Navigate to **Delta Live Tables**
2. Find `spotify_analytics_pipeline`
3. Click **Start**

### Deploy the Dashboard App

Quick start:

```bash
# 1. Update apps/spotify_dashboard/app.yaml with your SQL Warehouse ID
# Replace <your-warehouse-id> with your actual SQL Warehouse ID

# 2. Deploy the bundle
databricks bundle deploy -t dev
```

Access the app in Databricks UI → **Apps** → `spotify-dashboard-app`

**Alternatively, run locally:**
```bash
cd apps/spotify_dashboard
pip install -r requirements.txt

# Set environment variables
export DATABRICKS_SERVER_HOSTNAME="dbc-df2be2c9-07c1.cloud.databricks.com"
export DATABRICKS_HTTP_PATH="/sql/1.0/warehouses/<your-warehouse-id>"
export DATABRICKS_TOKEN="<your-token>"

# Run the app
streamlit run app.py
```

## Pipeline Structure

### Job: `spotify_data_loader_job` (Bronze Layer)

Two tasks that create the raw data layer:

1. **create_catalog_schema**: Sets up the Unity Catalog structure
   - Creates catalog `spotify_dev`
   - Creates schemas `main_schema` and `prod_schema`

2. **load_spotify_data**: Downloads and loads the data
   - Downloads Spotify Charts dataset from Kaggle
   - Loads CSV data into a Delta table (50K rows for dev speed)
   - Adds metadata columns (load_timestamp, source_file)
   - Creates table: `spotify_dev.main_schema.spotify_charts`

### DLT Pipeline: `spotify_dlt_pipeline` (Silver/Gold Layers)

Transforms raw data through quality checks and aggregations:

1. **Silver Table**: `spotify_charts_silver`
   - Formats date column properly
   - Drops unnecessary columns (load_timestamp, source_file, chart)
   - Validates no null values in critical fields
   - Extracts year, month, day components

2. **Gold Tables**: 
   - `spotify_charts_gold`: Aggregated metrics by artist, region, and month
   - `top_artists_by_region`: Top 100 artists per region per month

See [APP_SETUP.md](./APP_SETUP.md) for detailed pipeline documentation.

### Databricks App: `spotify_dashboard_app` (Interactive Analytics)

An interactive Streamlit dashboard for exploring the data:

**Features:**
- 📊 **Overview Dashboard**: Key metrics, regional breakdown, monthly trends
- 🎤 **Artist Performance**: Top artists, comparisons, detailed metrics
- 📈 **Chart Positions**: Daily chart tracking, song-level analysis

See [APP_SETUP.md](./APP_SETUP.md) for deployment instructions.

## Configuration

You can customize the catalog and schema names in `databricks.yml`:

```yaml
variables:
  catalog_name:
    default: spotify_dev
  schema_name:
    default: main_schema
```

## Monitoring

After deployment, you can monitor your job in the Databricks workspace:
- Navigate to **Workflows** → **Jobs**
- Find `spotify_data_loader_job`
- View run history and logs

## Notes

- The job is scheduled to run daily at midnight UTC but is initially paused
- The notebooks use single-node clusters for the setup task and a 2-worker cluster for data loading
- Data is loaded using `overwrite` mode, so each run will replace the existing data
- The kagglehub library is automatically installed via PyPI when the job runs

