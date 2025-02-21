import pandas as pd
import os

def check_excel_file(file_path):
    """Check the structure of an Excel file"""
    try:
        # Make sure the file exists
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} does not exist")
            return

        # Read the Excel file
        xl = pd.ExcelFile(file_path)
        
        # Get sheet names
        sheets = xl.sheet_names
        
        print(f"\nFile: {os.path.basename(file_path)}")
        print(f"Number of sheets: {len(sheets)}")
        print("\nSheet details:")
        
        for sheet in sheets:
            df = pd.read_excel(file_path, sheet_name=sheet)
            print(f"\nSheet: {sheet}")
            print(f"Dimensions: {df.shape[0]} rows × {df.shape[1]} columns")
            print("Columns:", list(df.columns))
            
            # Check for empty cells in first column
            empty_cells = df.iloc[:, 0].isna().sum()
            if empty_cells > 0:
                print(f"Warning: {empty_cells} empty cells found in first column")

    except Exception as e:
        print(f"Error processing file: {str(e)}")

if __name__ == '__main__':
    # Check all input Excel files
    input_dir = "data/input"
    for file in os.listdir(input_dir):
        if file.endswith('.xlsx'):
            check_excel_file(os.path.join(input_dir, file))
