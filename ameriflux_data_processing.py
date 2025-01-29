"""
This script processes the AmeriFlux BASE data by extracting, restructuring, and saving data
from the dataset. The script groups data by VARIABLE_GROUP, aligns date values, and exports
each group as a separate CSV file. If a group lacks a date column, the GROUP_ID is used instead.

Steps:
1. Load the AmeriFlux BASE data from an Excel file.
2. Extract relevant columns.
3. Identify and merge date values associated with each GROUP_ID.
4. If a date is missing, use the GROUP_ID as a replacement.
5. Remove redundant date rows to ensure data clarity.
6. Pivot the data to organize it by VARIABLE_GROUP.
7. Save each VARIABLE_GROUP as a separate CSV file for further analysis.

This script ensures efficient data transformation for biomass and soil research.
"""

import pandas as pd

# Load the Excel file
file_path = "AMF_US-Ne1_BIF_20230922.xlsx"  # Update with the correct file path
df = pd.read_excel(file_path, sheet_name="AMF-BIF")

# Extract relevant columns
df_filtered = df[["SITE_ID", "GROUP_ID", "VARIABLE_GROUP", "VARIABLE", "DATAVALUE"]]

# Extract date values from all VARIABLE_GROUP categories
df_dates = df_filtered[df_filtered["VARIABLE"].str.contains("DATE", na=False)][["GROUP_ID", "DATAVALUE"]]
df_dates.rename(columns={"DATAVALUE": "DATE"}, inplace=True)

# Merge dates with main data
df_merged = df_filtered.merge(df_dates, on="GROUP_ID", how="left")

# Rename columns to avoid KeyError due to column duplication
df_merged.rename(columns={"VARIABLE": "VARIABLE_x"}, inplace=True)

# Replace missing DATE values with GROUP_ID without triggering a FutureWarning
df_merged.loc[:, "DATE"] = df_merged["DATE"].fillna(df_merged["GROUP_ID"].astype(str))

# Remove date rows to avoid redundancy
df_cleaned = df_merged[~df_merged["VARIABLE_x"].str.contains("DATE", na=False)]

# Ensure no issues with unique values retrieval
if "VARIABLE_GROUP" in df_cleaned.columns:
    variable_groups = df_cleaned["VARIABLE_GROUP"].unique()
else:
    variable_groups = []

# Process each VARIABLE_GROUP separately
for group in variable_groups:
    df_group = df_cleaned[df_cleaned["VARIABLE_GROUP"] == group]
    df_pivot = df_group.pivot_table(index=["DATE"], columns="VARIABLE_x", values="DATAVALUE", aggfunc="first")
    df_pivot.reset_index(inplace=True)
    df_pivot.rename(columns={"DATE": "GROUP_ID"}, inplace=True)
    file_name = f"processed_{group}.csv"
    df_pivot.to_csv(file_name, index=False)
    print(f"Data processing complete. Saved as {file_name}")
