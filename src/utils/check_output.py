import pandas as pd
import os

def check_output_file(file_path):
    """Check the output Excel file for completeness"""
    try:
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"Error: Output file {file_path} not found")
            return
            
        # Read the Excel file
        df = pd.read_excel(file_path)
        
        # Expected columns that should have been added
        expected_columns = [
            '成立时间', '是否上市', '母公司', '母公司是否上市',
            '融资历史', '行业属性', '赛道名称', '创始人信息'
        ]
        
        # Check for missing columns
        missing_columns = [col for col in expected_columns if col not in df.columns]
        if missing_columns:
            print(f"Warning: Missing columns: {', '.join(missing_columns)}")
        
        # Check for empty cells in added columns
        for col in [c for c in expected_columns if c in df.columns]:
            empty_count = df[col].isna().sum()
            if empty_count > 0:
                print(f"Warning: {empty_count} empty cells in column '{col}'")
                
        print("Output file check completed")
        
    except Exception as e:
        print(f"Error checking output file: {str(e)}")

if __name__ == '__main__':
    # Check all output Excel files
    output_dir = "data/output"
    for file in os.listdir(output_dir):
        if file.endswith('_with_info.xlsx'):
            check_output_file(os.path.join(output_dir, file))
