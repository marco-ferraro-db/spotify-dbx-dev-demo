"""
Utility functions for data loading and workspace client management
"""

import streamlit as st
import pandas as pd
from databricks.sdk import WorkspaceClient
from databricks.sdk.service.sql import StatementState
import os

from config import CATALOG, SCHEMA


# Get warehouse ID from environment
WAREHOUSE_ID = os.getenv("WAREHOUSE_ID")


@st.cache_resource
def get_workspace_client():
    """Get Databricks Workspace Client"""
    if not WAREHOUSE_ID or WAREHOUSE_ID == "REPLACE_WITH_YOUR_WAREHOUSE_ID":
        st.error("❌ Warehouse ID not configured!")
        st.error("Please update `apps/spotify_dashboard/app.yaml` with your SQL Warehouse ID")
        st.info("Get your warehouse ID from: Databricks UI → SQL Warehouses → Click your warehouse → Copy ID from URL")
        st.stop()
    return WorkspaceClient()


@st.cache_data(ttl=300)
def load_data(query, limit=1000):
    """Load data from Unity Catalog"""
    try:
        w = get_workspace_client()
        
        # Add limit to query if not present
        if "LIMIT" not in query.upper():
            query = f"{query} LIMIT {limit}"
        
        result = w.statement_execution.execute_statement(
            statement=query,
            warehouse_id=WAREHOUSE_ID,
            catalog=CATALOG,
            schema=SCHEMA,
            wait_timeout="50s"
        )
        
        if result.status.state == StatementState.SUCCEEDED:
            if result.result and result.result.data_array:
                columns = [col.name for col in result.manifest.schema.columns]
                data = []
                for row in result.result.data_array:
                    row_data = []
                    for cell in row:
                        # Handle different data types
                        if isinstance(cell, str):
                            # Cell is already a string
                            row_data.append(cell)
                        elif hasattr(cell, 'str_value'):
                            # Cell is an object with str_value
                            if cell.str_value is not None:
                                row_data.append(cell.str_value)
                            elif hasattr(cell, 'int_value') and cell.int_value is not None:
                                row_data.append(cell.int_value)
                            elif hasattr(cell, 'float_value') and cell.float_value is not None:
                                row_data.append(cell.float_value)
                            else:
                                row_data.append(None)
                        else:
                            # Unknown type, convert to string
                            row_data.append(str(cell) if cell is not None else None)
                    data.append(row_data)
                return pd.DataFrame(data, columns=columns)
            return pd.DataFrame()
        else:
            error_msg = f"Query failed: {result.status.state}"
            if result.status.error:
                error_msg += f"\n{result.status.error.message}"
            st.error(error_msg)
            st.code(query, language="sql")
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return pd.DataFrame()

