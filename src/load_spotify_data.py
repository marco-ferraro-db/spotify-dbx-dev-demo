# Databricks notebook source
# MAGIC %md
# MAGIC # Load Spotify Charts Data
# MAGIC This notebook downloads the Spotify Charts dataset from Kaggle and loads it into a Delta table

# COMMAND ----------

# MAGIC %pip install kagglehub

# COMMAND ----------

dbutils.library.restartPython()

# COMMAND ----------

import kagglehub
import os
from pyspark.sql import SparkSession
from pyspark.sql.functions import *

# COMMAND ----------

# MAGIC %md
# MAGIC ## Configuration

# COMMAND ----------

catalog_name = "spotify_dev"
schema_name = "main_schema"
table_name = "spotify_charts"

# For faster development, set sample size (None = load all data)
# Set to a number like 10000 to load only that many rows
SAMPLE_SIZE = 250000  # Load only 50k rows for faster processing

# Set the catalog and schema
spark.sql(f"USE CATALOG {catalog_name}")
spark.sql(f"USE SCHEMA {schema_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Download Dataset from Kaggle

# COMMAND ----------

# Download latest version
path = kagglehub.dataset_download("dhruvildave/spotify-charts")
print("Path to dataset files:", path)

# COMMAND ----------

# MAGIC %md
# MAGIC ## List Downloaded Files

# COMMAND ----------

# List all files in the downloaded path
import glob

all_files = []
for root, dirs, files in os.walk(path):
    for file in files:
        file_path = os.path.join(root, file)
        all_files.append(file_path)
        print(f"Found file: {file_path}")

print(f"\nTotal files found: {len(all_files)}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Load Data into DataFrame

# COMMAND ----------

# Find CSV files
csv_files = [f for f in all_files if f.endswith('.csv')]
print(f"CSV files found: {len(csv_files)}")

if csv_files:
    # Read CSV with pandas from local filesystem
    import pandas as pd
    
    if len(csv_files) == 1:
        # Load single CSV file with optional sampling
        if SAMPLE_SIZE:
            pandas_df = pd.read_csv(csv_files[0], nrows=SAMPLE_SIZE)
            print(f"Loaded {len(pandas_df)} rows (sampled) from {csv_files[0]}")
        else:
            pandas_df = pd.read_csv(csv_files[0])
            print(f"Loaded {len(pandas_df)} rows (all data) from {csv_files[0]}")
    else:
        # Load and concatenate multiple CSV files
        dfs = []
        rows_loaded = 0
        for csv_file in csv_files:
            if SAMPLE_SIZE and rows_loaded >= SAMPLE_SIZE:
                break
            
            rows_to_read = None if not SAMPLE_SIZE else min(SAMPLE_SIZE - rows_loaded, SAMPLE_SIZE)
            temp_df = pd.read_csv(csv_file, nrows=rows_to_read)
            dfs.append(temp_df)
            rows_loaded += len(temp_df)
        
        pandas_df = pd.concat(dfs, ignore_index=True)
        sample_note = f" (sampled)" if SAMPLE_SIZE else " (all data)"
        print(f"Loaded {len(pandas_df)} rows{sample_note} from {len(csv_files)} files")
    
    # Convert pandas DataFrame to Spark DataFrame
    df = spark.createDataFrame(pandas_df)
    
    print("\nSchema:")
    df.printSchema()
    
    print("\nSample data:")
    df.show(5, truncate=False)
else:
    raise Exception("No CSV files found in the downloaded dataset")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Delta Table

# COMMAND ----------

# Add metadata columns
df_with_metadata = df \
    .withColumn("load_timestamp", current_timestamp()) \
    .withColumn("source_file", lit(path))

# Write to Delta table
full_table_name = f"{catalog_name}.{schema_name}.{table_name}"

df_with_metadata.write \
    .format("delta") \
    .mode("overwrite") \
    .option("overwriteSchema", "true") \
    .saveAsTable(full_table_name)

print(f"\n✅ Successfully created table: {full_table_name}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Verify Table Creation

# COMMAND ----------

# Query the table to verify
result_df = spark.sql(f"SELECT * FROM {full_table_name} LIMIT 10")
print(f"\nTable '{full_table_name}' contains {spark.table(full_table_name).count()} rows")
print("\nSample data from table:")
result_df.show(10, truncate=False)

# COMMAND ----------

# Show table properties
spark.sql(f"DESCRIBE EXTENDED {full_table_name}").show(truncate=False)

