"""
ameriflux_data_processing.py
Key Features:
2. Extract relevant columns for processing.
4. Handle missing date values by substituting GROUP_ID as a replacement.
- Load the Excel file containing AmeriFlux BASE data.
- Filter the dataset to include only relevant columns: SITE_ID, GROUP_ID, VARIABLE_GROUP, VARIABLE, and DATAVALUE.
- Extract and organize date information for each GROUP_ID.
- Process each VARIABLE_GROUP independently:
    - Extract data for the group.
    - Merge date information and other variables into a structured format.
    - Reorder columns to prioritize GROUP_ID and date columns.
    - Sort data by GROUP_ID and handle numeric conversion where applicable.
    - Save the processed data as a CSV file in the output directory.
- Display a sample of the processed data for verification.
Output:
- A directory named "processed_data" containing CSV files for each VARIABLE_GROUP.
- Each CSV file is structured with GROUP_ID, date columns, and other variables.
Dependencies:
- pandas: For data manipulation and processing.
- os: For directory and file handling.
Usage:
- Update the `file_path` variable with the correct path to the AmeriFlux BASE Excel file.
- Run the script to process the data and generate CSV files in the "processed_data" directory.
Note:
- Ensure the input Excel file contains a sheet named "AMF-BIF".
- Handle missing or malformed data gracefully during processing.
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
7. Convert GROUP_ID to numeric format when possible and sort it in ascending order.
8. Save each VARIABLE_GROUP as a separate CSV file for further analysis.

This script ensures efficient data transformation for biomass and soil research.
"""

import pandas as pd

# Load the Excel file
file_path = "./AMF_US-Ne1_BIF_20230922.xlsx"  # Update with the correct file path
df = pd.read_excel(file_path, sheet_name="AMF-BIF")

# Extract relevant columns
df_filtered = df[["SITE_ID", "GROUP_ID", "VARIABLE_GROUP", "VARIABLE", "DATAVALUE"]]

# Create a dictionary to store date information by GROUP_ID
date_info = {}

# Process date information first
date_rows = df_filtered[df_filtered["VARIABLE"].str.contains("DATE", na=False)]
for _, row in date_rows.iterrows():
    group_id = row["GROUP_ID"]
    variable = row["VARIABLE"]
    value = row["DATAVALUE"]
    
    if group_id not in date_info:
        date_info[group_id] = {}
    
    date_info[group_id][variable] = value

# Create a directory to store output files
output_dir = "processed_data"
os.makedirs(output_dir, exist_ok=True)

# Process each VARIABLE_GROUP separately
for group in df_filtered["VARIABLE_GROUP"].unique():
    print(f"Processing {group}...")
    
    # Filter data for the current group
    df_group = df_filtered[df_filtered["VARIABLE_GROUP"] == group]
    
    # Get unique GROUP_IDs for this variable group
    group_ids = df_group["GROUP_ID"].unique()
    
    # Create a list to store processed rows
    processed_rows = []
    
    for group_id in group_ids:
        # Get data for this GROUP_ID
        df_id = df_group[df_group["GROUP_ID"] == group_id]
        
        # Create a dictionary for this row
        row_dict = {"GROUP_ID": group_id}
        
        # Add date information if available
        if group_id in date_info:
            for date_var, date_val in date_info[group_id].items():
                row_dict[date_var] = date_val
        
        # Add non-date variables
        for _, row in df_id[~df_id["VARIABLE"].str.contains("DATE", na=False, regex=True)].iterrows():
            variable = row["VARIABLE"]
            value = row["DATAVALUE"]
            row_dict[variable] = value
        
        # Add to processed rows
        processed_rows.append(row_dict)
    
    # Create DataFrame from processed rows
    if processed_rows:
        result_df = pd.DataFrame(processed_rows)
        
        # Reorder columns to put GROUP_ID first, followed by date columns, then other variables
        cols = ["GROUP_ID"]
        date_cols = [col for col in result_df.columns if "DATE" in col]
        other_cols = [col for col in result_df.columns if col != "GROUP_ID" and col not in date_cols]
        
        # Combine columns in the desired order
        ordered_cols = cols + date_cols + other_cols
        
        # Filter to only include columns that actually exist in the DataFrame
        ordered_cols = [col for col in ordered_cols if col in result_df.columns]
        
        # Reorder columns
        result_df = result_df[ordered_cols]
        
        # Sort by GROUP_ID
        try:
            result_df["GROUP_ID"] = pd.to_numeric(result_df["GROUP_ID"], errors='coerce')
            result_df.sort_values(by="GROUP_ID", inplace=True)
            result_df["GROUP_ID"] = result_df["GROUP_ID"].fillna(0).astype(int).astype(str)
        except:
            result_df.sort_values(by="GROUP_ID", inplace=True)
        
        # Write to CSV
        output_file = os.path.join(output_dir, f"{group}.csv")
        result_df.to_csv(output_file, index=False)
        print(f"  - Created {output_file} with {len(result_df)} rows and {len(result_df.columns)} columns")
    else:
        print(f"  - No data to process for {group}")

print(f"\nProcessing complete. Results saved to the '{output_dir}' directory.")

# Optional: Display sample of a processed file to verify format
sample_group = df_filtered["VARIABLE_GROUP"].unique()[0]
sample_file = os.path.join(output_dir, f"{sample_group}.csv")
if os.path.exists(sample_file):
    print(f"\nSample of {sample_file}:")
    sample_df = pd.read_csv(sample_file)
    print(sample_df.head())