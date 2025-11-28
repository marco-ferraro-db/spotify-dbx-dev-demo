-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Spotify Charts Analytics - DLT SQL Pipeline
-- MAGIC 
-- MAGIC This Delta Live Tables pipeline transforms Spotify charts data from bronze to gold layers using SQL.

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Silver Layer: Daily Chart Positions (Cleaned)

-- COMMAND ----------

CREATE OR REFRESH LIVE TABLE daily_chart_positions
COMMENT "Silver layer: Daily chart positions with cleaned data and formatted dates"
TBLPROPERTIES ("quality" = "silver", "pipelines.autoOptimize.managed" = "true")
AS 
WITH source_data AS (
  SELECT
    title,
    CAST(rank AS INT) AS rank,
    CAST(date AS DATE) AS chart_date,
    YEAR(date) AS year,
    MONTH(date) AS month,
    DAYOFMONTH(date) AS day,
    artist,
    url,
    region,
    trend,
    CAST(streams AS BIGINT) AS streams,
    CURRENT_TIMESTAMP() AS processed_timestamp
  FROM spotify_dev.main_schema.spotify_charts
)
SELECT *
FROM source_data
WHERE title IS NOT NULL
  AND rank IS NOT NULL
  AND chart_date IS NOT NULL
  AND artist IS NOT NULL;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Gold Layer: Monthly Artist Performance by Region

-- COMMAND ----------

CREATE OR REFRESH LIVE TABLE monthly_artist_performance (
  CONSTRAINT valid_total_streams EXPECT (total_streams > 0),
  CONSTRAINT valid_avg_rank EXPECT (avg_rank > 0)
)
COMMENT "Gold layer: Monthly aggregated performance metrics by artist and region"
TBLPROPERTIES ("quality" = "gold", "pipelines.autoOptimize.managed" = "true")
AS SELECT
  artist,
  region,
  year,
  month,
  SUM(streams) AS total_streams,
  AVG(rank) AS avg_rank,
  MIN(rank) AS best_rank,
  MAX(rank) AS worst_rank,
  COUNT(*) AS chart_appearances,
  COUNT(DISTINCT title) AS unique_songs,
  MIN(chart_date) AS period_start_date,
  CURRENT_TIMESTAMP() AS last_updated
FROM LIVE.daily_chart_positions
GROUP BY artist, region, year, month;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Gold Layer: Monthly Top 100 Artists by Region

-- COMMAND ----------

CREATE OR REFRESH LIVE TABLE monthly_top_100_artists
COMMENT "Gold layer: Top 100 performing artists per region per month, ranked by total streams"
TBLPROPERTIES ("quality" = "gold", "pipelines.autoOptimize.managed" = "true")
AS SELECT
  artist,
  region,
  year,
  month,
  total_streams,
  avg_rank,
  best_rank,
  worst_rank,
  chart_appearances,
  unique_songs,
  period_start_date,
  last_updated,
  ROW_NUMBER() OVER (
    PARTITION BY region, year, month 
    ORDER BY total_streams DESC
  ) AS rank_in_region
FROM LIVE.monthly_artist_performance
QUALIFY rank_in_region <= 100;

