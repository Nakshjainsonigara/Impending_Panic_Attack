import pandas as pd

def process_survey_data(file_path, sum_score_keyword, output_file_name,custom_sum_col=None):
    """
    Process survey data to clean and compute mean sum scores per ID.

    Parameters:
    - file_path (str): Path to the input CSV file.
    - output_path (str): Path to save the cleaned CSV.
    - id_abbreviation (str): Substring to filter valid IDs (e.g., "SYM").
    - sum_score_keyword (str): Keyword to detect the sum score column (e.g., "depression_sum_score").
    """

    # Step 1: Read CSV
    df = pd.read_excel(file_path)
    print(f"Initial Shape: {df.shape}")

    # Step 2: Lowercase all column names
    df.columns = df.columns.str.lower()
    df=df.rename(columns={"non-identifying keys":"id"})

    if custom_sum_col:
        sum_col = custom_sum_col.lower()
        df = df.rename(columns={sum_col: sum_score_keyword})
    else:
        # Automatically detect sum_col if no custom column is specified
        sum_col = next((col for col in df.columns if "sum" in col), None) or \
                  next((col for col in df.columns if "total" in col), None) or \
                  next((col for col in df.columns if "combined" in col), None)
        if not sum_col:
            print("Numeric Sum metric missing, file cannot be processed")
            return None
        else:
            df = df.rename(columns={sum_col: sum_score_keyword})

    # Step 4: Drop rows where all non-metadata columns are NaN
    meta_cols = ["id", "survey start date", "survey end date", "survey completion date", "survey skipped"]
    subset_cols = df.columns[~df.columns.isin(meta_cols)]
    df = df.dropna(axis=0, subset=subset_cols, how="all")

    print(f"After Dropping Empty Rows: {df.shape}")

    # Step 5: Drop rows where ID is missing
    df = df.dropna(subset=["id"])
    print(f"After Dropping Missing IDs: {df.shape}")

    # Step 6: Keep only IDs containing the given abbreviation
    df = df[df["id"].astype(str).str.contains("SYM", na=False)]
    print(f"After Filtering by ID: {df.shape}")

    # Step 7: Check missing values in sum score column
    missing_sum_score = df[sum_score_keyword].isna().sum()
    print(f"Missing Values in {sum_score_keyword}: {missing_sum_score}")

    if missing_sum_score > 0:
        print("Warning: There are missing values in the sum score column!")
    if missing_sum_score==len(df):
        print("All files in the data frame are missing file cannot be processed")
        return None

    # Step 8: Pivot table to compute mean sum score per ID
    df = df.pivot_table(index="id", values=sum_score_keyword, aggfunc="mean")
    print(f"After Pivoting: {df.shape}")

    # Step 9: Save the final cleaned CSV
    output_path = "../data_processed/"+output_file_name
    df.to_csv(output_path, index=False)
    print(f"Process completed. File saved at {output_path}")
    return df