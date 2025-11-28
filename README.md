# 🎵 Spotify Charts Analytics with Databricks

A complete end-to-end data analytics project using Databricks Asset Bundles (DABs) to load, transform, and visualize Spotify Charts data through a medallion architecture with Delta Live Tables and an interactive AI-powered dashboard.

> ✅ **Works with Databricks Free Tier!**

## 🚀 Quick Start Guide

### Prerequisites

1. **Databricks Account** (Free tier works!)
   - Sign up at [databricks.com/try-databricks](https://databricks.com/try-databricks)
   - Use Community Edition or Free Trial

2. **Databricks CLI**
   ```bash
   pip install databricks-cli
   ```

3. **Configure Authentication**
   ```bash
   databricks configure --token
   ```
   - **Host**: Your workspace URL (e.g., `https://dbc-xxx.cloud.databricks.com`)
   - **Token**: Generate from User Settings → Access Tokens

### 📋 Execution Steps

Follow these steps in order:

#### **Step 1: Deploy the Bundle**
```bash
cd spotify-dbx-dev-demo
databricks bundle deploy -t dev
```

#### **Step 2: Create Catalog & Schema**
```bash
databricks bundle run spotify_data_loader -t dev
```
This job has 2 tasks:
- Creates catalog `spotify_dev` and schemas `main_schema` & `prod_schema`
- Loads Spotify Charts data from Kaggle (50K rows for speed)

⏱️ Takes ~5-10 minutes

#### **Step 3: Run DLT Pipeline**
```bash
databricks pipelines start spotify-analytics-pipeline
```
Or from UI: **Delta Live Tables** → `spotify-analytics-pipeline` → **Start**

Creates 3 tables in `prod_schema`:
- `daily_chart_positions` (Silver)
- `monthly_artist_performance` (Gold)
- `monthly_top_100_artists` (Gold)

⏱️ Takes ~5-10 minutes

#### **Step 4: Configure & Launch the App**

1. **Get your SQL Warehouse ID**:
   - Databricks UI → **SQL Warehouses**
   - Click your warehouse → Copy ID from URL

2. **Update app configuration**:
   ```bash
   # Edit apps/spotify_dashboard/app.yaml
   # Replace WAREHOUSE_ID value with your actual warehouse ID
   ```

3. **Redeploy to apply changes**:
   ```bash
   databricks bundle deploy -t dev
   ```

4. **Access the app**:
   - Databricks UI → **Apps** → `spotify-dashboard-app`
   - Wait 1-2 minutes for startup
   - Click "Open App"

🎉 **Done!** You now have a fully functional Spotify analytics dashboard!

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

## 🎯 What You'll Build

This project demonstrates:

- **📥 Data Ingestion**: Automated loading from Kaggle
- **🏗️ Medallion Architecture**: Bronze → Silver → Gold layers
- **🔄 Delta Live Tables**: Declarative data transformations with quality checks
- **📊 Interactive Dashboard**: Streamlit app with 4 analytical views
- **🤖 AI Assistant**: LLM-powered chatbot for data insights
- **🚀 Infrastructure as Code**: Everything deployed with Databricks Asset Bundles

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



## 📂 Project Architecture

```
Bronze Layer (main_schema)     Silver Layer (prod_schema)      Gold Layer (prod_schema)
────────────────────────       ─────────────────────────       ─────────────────────────
spotify_charts              →   daily_chart_positions       →   monthly_artist_performance
(raw Kaggle data)              (cleaned & validated)           monthly_top_100_artists
                                                               (aggregated metrics)
```

## ⚙️ Configuration

**Catalog & Schemas** (`databricks.yml`):
```yaml
variables:
  catalog_name: spotify_dev
  schema_name: main_schema
  prod_schema_name: prod_schema
```

**Sample Size** (`src/load_spotify_data.py`):
- Default: 50,000 rows (fast for development)
- Change `SAMPLE_SIZE = None` to load all data

## 📊 Key Components

| Component | Type | Description |
|-----------|------|-------------|
| `spotify_data_loader` | Job | Creates catalog/schema & loads Kaggle data |
| `spotify-analytics-pipeline` | DLT Pipeline | Transforms data (Bronze→Silver→Gold) |
| `spotify-dashboard-app` | Databricks App | Interactive analytics dashboard |


## 📝 License

This is a demo project for learning purposes.

