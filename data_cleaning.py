import pandas as pd

# errors='ignore' in .drop():
#     If a column in your list doesn't exist, Pandas will simply skip it without 
#     throwing an error. This makes the code much shorter and easier to maintain 
#     if you decide to drop more columns later.

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
    
def read_csv_file(file_path: str) -> pd.DataFrame:
    """Loads a CSV file and prints its structural information."""
    df = pd.read_csv(file_path)
    
    print('=====================================')
    print('DataFrame Columns')
    print(df.columns)
    print('=====================================')
    df.info()  # df.info() prints automatically; no need to wrap it in print()
    
    return df
    