#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run the full ETL process for all companies in the input files
"""

import os
from src.api_clients.xiniu_api_client import process_excel_file

def main():
    """
    Process all Excel files in the input directory
    """
    input_dir = "data/input"
    
    # Get all Excel files in the input directory
    input_files = [f for f in os.listdir(input_dir) if f.endswith('.xlsx') and not f.startswith('~$')]
    
    print(f"Found {len(input_files)} Excel files to process")
    
    # Process each file
    for file_name in input_files:
        input_file = os.path.join(input_dir, file_name)
        print(f"\nProcessing file: {file_name}")
        process_excel_file(input_file)
        
    print("\nAll files processed successfully!")

if __name__ == "__main__":
    main()
