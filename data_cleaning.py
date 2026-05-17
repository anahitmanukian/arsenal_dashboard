import os
import glob
import pandas as pd

# ==========================================
# 1. Your Core Cleaning Helper Functions
# ==========================================

def drop_cols(df: pd.DataFrame) -> pd.DataFrame:
    """Drops specific unwanted columns if they exist in the DataFrame."""
    cols_to_drop = ['Notes', 'Rk', 'Match Report']
    return df.drop(columns=cols_to_drop, errors='ignore')
        
def drop_null_dates(df: pd.DataFrame) -> pd.DataFrame:
    """Removes rows where the 'Date' column is null and resets the index."""
    return df.dropna(subset=['Date']).reset_index(drop=True)
    
def remove_repeated_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Filters out rows where the 'Date' column contains header text or specific strings."""
    return df[~df['Date'].isin(['Date', 'For Arsenal'])]
    
def load_csv_with_wrong_headers(file_path: str) -> pd.DataFrame:
    """Loads a CSV, skipping the very first row and using the second row as the header."""
    return pd.read_csv(file_path, header=0, skiprows=[0])

# ==========================================
# 2. Automated Pipeline Functions
# ==========================================

def clean_and_save_data(paths: list[str], is_match_log: bool = False, output_base: str = "data/processed"):
    """
    Loops through raw CSV paths, cleans the data, and saves them into a parallel 
    folder structure inside data/processed to preserve the source context.
    """
    for path in paths:
        # Step 1: Extract the folder name and file name to preserve identity
        folder_name = os.path.basename(os.path.dirname(path)) 
        file_name = os.path.basename(path)                  
        
        # --- NEW STEP 1.5: Skip table_8.csv if we are dealing with scores/fixtures ---
        if "scores" in folder_name and file_name == "table_8.csv":
            print(f"Skipping junk file: {folder_name}/{file_name}")
            continue

        # Step 2: Load the data correctly depending on type
        # Match logs use custom headers, but scores and goals use standard read_csv
        if is_match_log:
            df = load_csv_with_wrong_headers(path) 
        else:
            df = pd.read_csv(path)
            
        # Step 3: Run your data cleaning chain (Assigning back to df!)
        # remove_repeated_rows(df) automatically drops line 27 where headers repeat!
        df = drop_cols(df)
        df = drop_null_dates(df)
        df = remove_repeated_rows(df)
        
        # Step 4: Create the new matching directory path inside processed/
        target_dir = os.path.join(output_base, folder_name)
        os.makedirs(target_dir, exist_ok=True)
        
        # Step 5: Save it at the end of the loop iteration
        # Renaming table_9.csv to something meaningful makes downstream RAG cleaner
        final_file_name = "scores_and_fixtures_cleaned.csv" if file_name == "table_9.csv" else file_name
        output_path = os.path.join(target_dir, final_file_name)
        
        df.to_csv(output_path, index=False)
        print(f"Processed & Saved: {output_path}")


# ==========================================
# 3. Execution Entry Point
# ==========================================
if __name__ == "__main__":
    
    print("--- Searching for Raw Files ---")
    
    # Captures anything containing 'goal_logs' inside data/raw/
    raw_goal_log_paths = glob.glob("data/raw/**/*goal_logs*/**/*.csv", recursive=True)
    
    # Captures anything containing 'match_logs' inside data/raw/
    raw_match_log_paths = glob.glob("data/raw/**/*match_logs*/**/*.csv", recursive=True)
    
    # NEW: Captures your new score and fixture folders for Prem and Champions League
    raw_score_paths = glob.glob("data/raw/**/*scores*/**/*.csv", recursive=True)
    
    print(f"Found {len(raw_goal_log_paths)} Goal Log CSV files.")
    print(f"Found {len(raw_match_log_paths)} Match Log CSV files.")
    print(f"Found {len(raw_score_paths)} Scores/Fixtures CSV files.")
    print("-" * 40)

    print("--- Starting Goal Logs Cleaning ---")
    if raw_goal_log_paths:
        clean_and_save_data(raw_goal_log_paths, is_match_log=False)
    else:
        print("No goal log files found.")
        
    print("\n--- Starting Match Logs Cleaning ---")
    if raw_match_log_paths:
        clean_and_save_data(raw_match_log_paths, is_match_log=True)
    else:
        print("No match log files found.")

    print("\n--- Starting Scores & Fixtures Cleaning ---")
    if raw_score_paths:
        # These load normally like goal logs, so is_match_log = False
        clean_and_save_data(raw_score_paths, is_match_log=False)
    else:
        print("No scores or fixtures files found.")  
               
    