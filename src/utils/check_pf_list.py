import pandas as pd
import os

def check_pf_list(file_path="data/input/PF Tracked List.xlsx"):
    """Check the peer funds list for completeness"""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Error: PF Tracked List file {file_path} not found")
            return
            
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        # Check if there are any entries
        if len(df) == 0:
            print("Warning: PF Tracked List is empty")
            return
            
        # Print summary
        print(f"\nFound {len(df)} peer funds")
        print(f"Columns: {', '.join(df.columns)}")
        
        # Check for empty cells
        for col in df.columns:
            empty_count = df[col].isna().sum()
            if empty_count > 0:
                print(f"Warning: {empty_count} empty cells in column '{col}'")
                
    except Exception as e:
        print(f"Error checking PF list: {str(e)}")

if __name__ == "__main__":
    check_pf_list()
