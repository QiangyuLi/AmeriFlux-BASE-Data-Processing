# AmeriFlux BASE Data Processing

This Python script processes the AmeriFlux BASE data by extracting, restructuring, and saving the data in a more usable format for analysis. It groups data by `VARIABLE_GROUP`, aligns date values, and exports each group as a separate CSV file. If a group lacks a date column, it uses the `GROUP_ID` as a substitute.

## Features

- **Data Extraction**: Extract relevant columns from the AmeriFlux BASE dataset (such as `SITE_ID`, `GROUP_ID`, `VARIABLE_GROUP`, `VARIABLE`, and `DATAVALUE`).
- **Date Handling**: Extract date values associated with each `GROUP_ID` and merge them into the main dataset.
- **Missing Data Handling**: If a date value is missing, it will replace it with the corresponding `GROUP_ID` value to maintain data consistency.
- **Data Pivoting**: Organize data by `VARIABLE_GROUP` for easy analysis.
- **CSV Export**: Export each `VARIABLE_GROUP` as a separate CSV file for further analysis.

## Requirements

This script requires the following Python libraries:

- **pandas**: A powerful Python library for data manipulation and analysis.

To install the required dependencies, run the following command:

```bash
pip install pandas
```

## Input Data Format

The script assumes the input data is an Excel file (`AMF_US-Ne1_BIF_20230922.xlsx`) containing the sheet named `"AMF-BIF"`. The sheet should have the following columns:

- `SITE_ID`: Identifies the site of the data.
- `GROUP_ID`: Identifies the group of the data (used to replace missing date values).
- `VARIABLE_GROUP`: The variable grouping for the dataset.
- `VARIABLE`: Specifies the variable name (e.g., temperature, humidity).
- `DATAVALUE`: The actual data value for the given `VARIABLE` and `GROUP_ID`.


## Steps Performed by the Script

1. **Load Data**: The script loads the Excel file and reads the sheet "AMF-BIF" into a pandas DataFrame.

```python
df = pd.read_excel(file_path, sheet_name="AMF-BIF")
```

2. **Extract Relevant Columns**: The script extracts the following columns from the loaded data: SITE_ID, GROUP_ID, VARIABLE_GROUP, VARIABLE, and DATAVALUE.

```python
df_filtered = df[["SITE_ID", "GROUP_ID", "VARIABLE_GROUP", "VARIABLE", "DATAVALUE"]]
```

3. **Extract and Merge Date Values**: The script extracts date values associated with each GROUP_ID. It merges these date values into the main dataset.

```python
df_dates = df_filtered[df_filtered["VARIABLE"].str.contains("DATE", na=False)][["GROUP_ID", "DATAVALUE"]]
df_dates.rename(columns={"DATAVALUE": "DATE"}, inplace=True)
df_merged = df_filtered.merge(df_dates, on="GROUP_ID", how="left")
```

4. **Handle Missing Date Values**: If the date value is missing, it is replaced with the GROUP_ID. This ensures that there is no missing date in the data.

```python
df_merged.loc[:, "DATE"] = df_merged["DATE"].fillna(df_merged["GROUP_ID"].astype(str))
```

5. **Remove Redundant Date Rows**: The script removes the rows containing DATE values from the VARIABLE column to ensure the data is clean and non-redundant.

```python
df_cleaned = df_merged[~df_merged["VARIABLE_x"].str.contains("DATE", na=False)]
```

6. **Pivot Data by VARIABLE_GROUP**: The script groups the data by VARIABLE_GROUP and pivots it so that the variables become columns, with the DATE values as the index.

```python
df_pivot = df_group.pivot_table(index=["DATE"], columns="VARIABLE_x", values="DATAVALUE", aggfunc="first")
df_pivot.reset_index(inplace=True)
```

7. **Save Each VARIABLE_GROUP to a CSV File**: Finally, the script saves each VARIABLE_GROUP as a separate CSV file named processed_<VARIABLE_GROUP>.csv.

```python
file_name = f"processed_{group}.csv"
df_pivot.to_csv(file_name, index=False)
```

## Usage Instructions

1. **Prepare Input File**: Ensure the input Excel file (AMF_US-Ne1_BIF_20230922.xlsx) is available in the same directory as the script. If the file is located elsewhere, update the file_path variable in the script to point to the correct location.

2. **Run the Script**: Execute the script in your terminal or command prompt using the following command:

```bash
python ameriflux_data_processing.py
```

3. **Check Output Files**: The script will generate separate CSV files for each VARIABLE_GROUP. The output files will be named as processed_<VARIABLE_GROUP>.csv.

## Example Output

If your data contains multiple variable groups, the output files will be named like:
- processed_VariableGroup1.csv
- processed_VariableGroup2.csv
- processed_VariableGroup3.csv

Each CSV file will contain the pivoted data with DATE as the index and variables as columns.

## Notes

- **Handling Missing Dates**: If the date value for a specific GROUP_ID is missing, the script will replace it with the GROUP_ID to ensure no data is lost.
- **Input Format**: The script expects the input Excel file to have a sheet named "AMF-BIF". The input data should be structured as described in the Input Data Format section.
- **Pivoting**: The data will be pivoted based on the DATE and VARIABLE_x columns, with the DATAVALUE filled in accordingly.

## License

This project is licensed under the MIT License - see the LICENSE file for details.