import pandas as pd
import os

def find_last_processed_row(df):
    """Find the last row that has data in the generated columns"""
    generated_columns = ['成立时间', '是否上市', '母公司', '母公司是否上市', '融资历史', 'Peer Fund',
                        '某一年融资超2次', '单轮3家以上fund', '2家以上Peer Fund', '已在Deal List',
                        '行业属性', '赛道名称', '产品/公司介绍', '创始人信息', '是否是股份公司', '股改时间']
    
    # Check which columns exist in the DataFrame
    existing_columns = [col for col in generated_columns if col in df.columns]
    if not existing_columns:
        return -1
    
    # Check which rows have data in the existing generated columns
    has_data = df[existing_columns].notna().any(axis=1)
    if not has_data.any():
        return -1
    
    # Find the last row with data
    last_processed = has_data[has_data].index[-1]
    return last_processed

def check_unfinished_rows(input_file):
    """Check for unfinished rows in each sheet after the last processed row"""
    print(f"\nChecking unfinished rows in: {input_file}")
    
    # Read all sheets
    xl = pd.ExcelFile(input_file)
    sheets = xl.sheet_names
    
    total_unfinished = 0
    sheet_results = []
    
    for sheet in sheets:
        df = pd.read_excel(input_file, sheet_name=sheet)
        
        # Find company name column
        company_name_column = '示范企业名称' if '示范企业名称' in df.columns else '企业名称'
        if company_name_column not in df.columns:
            for col in df.columns:
                if '名称' in col or 'name' in col.lower() or '企业' in col:
                    company_name_column = col
                    break
            if company_name_column not in df.columns:
                print(f"Warning: Could not find company name column in sheet {sheet}")
                continue
        
        # Find last processed row
        last_processed = find_last_processed_row(df)
        if last_processed == -1:
            print(f"\nSheet: {sheet}")
            print("No processed rows found")
            continue
        
        # Check for unfinished rows after the last processed row
        remaining_df = df.iloc[last_processed + 1:]
        unfinished = remaining_df[remaining_df[company_name_column].notna()]
        
        result = {
            'sheet': sheet,
            'last_processed_row': last_processed + 1,  # Convert to 1-based indexing
            'total_rows': len(df),
            'unfinished_rows': len(unfinished),
            'first_5_companies': []
        }
        
        if len(unfinished) > 0:
            result['first_5_companies'] = [
                (idx + 1, row[company_name_column]) 
                for idx, row in unfinished.head().iterrows()
            ]
        
        sheet_results.append(result)
        total_unfinished += len(unfinished)
    
    # Print results in a clear format
    print("\nDetailed Results:")
    print("=" * 80)
    
    for result in sheet_results:
        print(f"\nSheet: {result['sheet']}")
        print(f"Last processed row: {result['last_processed_row']}")
        print(f"Total rows in sheet: {result['total_rows']}")
        print(f"Unfinished rows after last processed: {result['unfinished_rows']}")
        
        if result['first_5_companies']:
            print("\nFirst 5 unfinished companies:")
            for row_num, company in result['first_5_companies']:
                print(f"Row {row_num}: {company}")
        print("-" * 80)
    
    print(f"\nTotal unfinished rows across all sheets: {total_unfinished}")

if __name__ == "__main__":
    input_file = "data/output/小巨人list copy_formatted.xlsx"
    check_unfinished_rows(input_file)
