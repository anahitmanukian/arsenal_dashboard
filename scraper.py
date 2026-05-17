import os
import glob
from bs4 import BeautifulSoup, Comment
from io import StringIO
import pandas as pd

def parse_tables_from_html(html_content: str) -> list[pd.DataFrame]:
    """
    Finds all tables in the HTML, including those hidden inside comments,
    and returns them as a list of Pandas DataFrames.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    dfs = []

    # 1. Grab standard visible tables
    visible_tables = soup.find_all("table")
    for table in visible_tables:
        try:
            df = pd.read_html(StringIO(str(table)))[0]
            dfs.append(df)
        except Exception:
            continue

    # 2. Extract tables hidden inside HTML comments
    comments = soup.find_all(string=lambda text: isinstance(text, Comment))
    for comment in comments:
        if "<table" in comment.lower():
            comment_soup = BeautifulSoup(comment, "html.parser")
            commented_tables = comment_soup.find_all("table")
            for table in commented_tables:
                try:
                    df = pd.read_html(StringIO(str(table)))[0]
                    dfs.append(df)
                except Exception:
                    continue
                    
    return dfs

def extract_and_save_fixtures(file_paths: list[str], output_base_dir: str = "data/raw", keep_last_n: int = 2):
    """
    Processes local FBref HTML files, extracts the relevant end tables, 
    and saves them cleanly directly to the data/raw folder.
    """
    for file_path in file_paths:
        print(f"Processing: {os.path.basename(file_path)}")
        
        with open(file_path, "r", encoding="utf-8") as f:
            html = f.read()

        # Parse all tables (visible + hidden)
        all_dfs = parse_tables_from_html(html)
        total_tables = len(all_dfs)
        print(f"Found total of {total_tables} tables (including commented ones).")

        if total_tables == 0:
            print(f"Skipping {file_path}: No tables found.")
            continue

        # Target the exact tables you actually need
        # If a file only needs the last 1 (like premier league fixtures), pass keep_last_n=1
        target_dfs = all_dfs[-keep_last_n:]
        
        # Create a clean folder name based on the HTML file name
        folder_name = os.path.splitext(os.path.basename(file_path))[0]
        folder_name = folder_name.lower().replace(" ", "_")
        
        target_dir = os.path.join(output_base_dir, folder_name)
        os.makedirs(target_dir, exist_ok=True)

        # Save only the relevant tables
        for idx, df in enumerate(target_dfs):
            # Using the actual index relative to the end tables
            table_num = total_tables - keep_last_n + idx
            csv_path = os.path.join(target_dir, f"table_{table_num}.csv")
            
            df.to_csv(csv_path, index=False)
            print(f"Saved targeted file: {csv_path}")
            
        print("=" * 50)

# Example usage:
if __name__ == "__main__":
    # Get all HTML files from your raw html directory
    html_folder = "data/raw/html"  # Adjust this to where your .html files sit
    local_html_files = glob.glob(f"{html_folder}/*.html")
    
    if local_html_files:
        # If most need the last 2, default to 2
        extract_and_save_fixtures(local_html_files, output_base_dir="data/raw", keep_last_n=2)