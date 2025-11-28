# Databricks notebook source
# MAGIC %md
# MAGIC # Setup Catalog and Schema
# MAGIC This notebook creates the catalog and schema for the Spotify data

# COMMAND ----------

catalog_name = "spotify_dev"
schema_name = "main_schema"
prod_schema_name = "prod_schema"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Catalog

# COMMAND ----------

# Create catalog if it doesn't exist
spark.sql(f"CREATE CATALOG IF NOT EXISTS {catalog_name}")
print(f"Catalog '{catalog_name}' created or already exists")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Create Schemas

# COMMAND ----------

# Create main schema if it doesn't exist
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog_name}.{schema_name}")
print(f"Schema '{catalog_name}.{schema_name}' created or already exists")

# Create prod schema if it doesn't exist
spark.sql(f"CREATE SCHEMA IF NOT EXISTS {catalog_name}.{prod_schema_name}")
print(f"Schema '{catalog_name}.{prod_schema_name}' created or already exists")

# COMMAND ----------

# Set the current catalog and schema
spark.sql(f"USE CATALOG {catalog_name}")
spark.sql(f"USE SCHEMA {schema_name}")
print(f"Using catalog '{catalog_name}' and schema '{schema_name}'")

# COMMAND ----------

# Verify setup
print("\n=== Current Database Configuration ===")
print(f"Current Catalog: {spark.sql('SELECT current_catalog()').collect()[0][0]}")
print(f"Current Schema: {spark.sql('SELECT current_schema()').collect()[0][0]}")

