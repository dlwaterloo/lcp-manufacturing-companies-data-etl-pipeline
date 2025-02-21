import pandas as pd

def check_output(file_path):
    """
    Check the contents of the output Excel file
    """
    # Read the Excel file
    df = pd.read_excel(file_path)
    
    print(f"\nFound {len(df)} companies with the following columns:")
    print("\nColumns:")
    for col in df.columns:
        print(f"- {col}")
    
    print("\nFirst company example:")
    first_company = df.iloc[0]
    for col in df.columns:
        print(f"\n{col}:")
        print(first_company[col])

if __name__ == "__main__":
    file_path = "1-6批制造业单项冠军 copy_with_info.xlsx"
    check_output(file_path)
