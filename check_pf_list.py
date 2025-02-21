import pandas as pd

def check_pf_list(file_path):
    """
    Check the contents of the PF Tracked List Excel file
    """
    # Read the Excel file without headers
    df = pd.read_excel(file_path, header=None)
    
    print(f"\nFound {len(df)} companies in the list:")
    print("\nFirst 10 companies:")
    for i, company in enumerate(df[0][:10], 1):
        print(f"{i}. {company}")
    
    print(f"\n... and {len(df) - 10} more companies")

if __name__ == "__main__":
    file_path = "PF Tracked List.xlsx"
    check_pf_list(file_path)
