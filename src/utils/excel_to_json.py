#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Convert Excel files to JSON files containing just the company names
"""

import pandas as pd
import json
import os

def convert_deallog_to_json(input_file="data/input/Deallog List.xlsx", output_file="data/input/deallog_companies.json"):
    """
    Convert Deallog List Excel file to a JSON file containing just the company names
    """
    try:
        # Read the Excel file
        df = pd.read_excel(input_file)
        
        # Get company names from first column, remove any leading/trailing whitespace
        company_names = [name.strip() for name in df.iloc[:, 0].dropna().tolist()]
        
        # Sort the company names for better readability
        company_names.sort()
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write to JSON file with proper Chinese character encoding
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(company_names, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully converted {len(company_names)} companies to {output_file}")
        
    except Exception as e:
        print(f"Error converting Excel to JSON: {str(e)}")

def convert_pf_to_json(input_file="data/input/PF Tracked List.xlsx", output_file="data/input/pf_companies.json"):
    """
    Convert PF Tracked List Excel file to a JSON file containing just the fund names
    """
    try:
        # Read the Excel file
        df = pd.read_excel(input_file)
        
        # Get fund names from first column, remove any leading/trailing whitespace
        fund_names = [name.strip() for name in df.iloc[:, 0].dropna().tolist()]
        
        # Sort the fund names for better readability
        fund_names.sort()
        
        # Create output directory if it doesn't exist
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Write to JSON file with proper Chinese character encoding
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(fund_names, f, ensure_ascii=False, indent=2)
            
        print(f"Successfully converted {len(fund_names)} funds to {output_file}")
        
    except Exception as e:
        print(f"Error converting Excel to JSON: {str(e)}")

if __name__ == "__main__":
    convert_deallog_to_json()
    convert_pf_to_json()
