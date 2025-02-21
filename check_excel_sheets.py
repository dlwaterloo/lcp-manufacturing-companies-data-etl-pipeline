import pandas as pd

def check_excel_sheets(file_path):
    """
    Check how many sheets are in the Excel file and their basic info
    """
    # Read the Excel file without loading any specific sheet
    excel_file = pd.ExcelFile(file_path)
    
    # Get sheet names
    sheet_names = excel_file.sheet_names
    print(f"\nFound {len(sheet_names)} sheets in {file_path}:")
    
    # Print info for each sheet
    for idx, sheet_name in enumerate(sheet_names, 1):
        # Read the sheet
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        num_rows = len(df)
        num_cols = len(df.columns)
        print(f"\n{idx}. Sheet: {sheet_name}")
        print(f"   Rows: {num_rows}")
        print(f"   Columns: {num_cols}")
        print(f"   Column names: {', '.join(df.columns.tolist())}")

if __name__ == "__main__":
    file_path = "1-6批制造业单项冠军 copy.xlsx"
    check_excel_sheets(file_path)
