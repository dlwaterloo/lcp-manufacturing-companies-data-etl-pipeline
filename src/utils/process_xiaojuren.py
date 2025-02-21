# coding=utf-8

import hashlib
import time
import requests
import pandas as pd
import sys
import os

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.api_clients.xiniu_api_client import (
    accesskeyid,
    signature_handler,
    get_company_info,
    get_company_id
)

def process_xiaojuren_list(input_file="data/input/小巨人list copy.xlsx", num_rows=10):
    """
    Process the first num_rows of the 小巨人 Excel file and add company information columns
    """
    try:
        print(f"Reading Excel file: {input_file}")
        df = pd.read_excel(input_file)
        
        # Take only the first num_rows
        df = df.head(num_rows)
        
        # Get the company full names from the Excel file
        company_names = df['企业名称'].tolist()  # Assuming the column name is '企业名称'
        total_companies = len(company_names)
        print(f"Processing first {total_companies} companies")
        
        # Create a dictionary to store company information
        company_info_dict = {}
        
        # Process each company
        for idx, company_name in enumerate(company_names, 1):
            print(f"\nProcessing company {idx}/{total_companies}: {company_name}")
            
            # Get company ID
            baseurl = 'https://api.xiniudata.com/openapi/v2/company/id/list_by_fullname'
            payload = {"fullName": company_name}
            
            reqData = {
                'version': 'v1',
                'accesskeyid': accesskeyid,
                'clientUserId': '',
                'signatureversion': 'v1',
                'payload': payload,
                'timestamp': str(round(time.time()))
            }
            
            reqData.update({'signature': signature_handler(reqData)})
            
            try:
                response = requests.post(baseurl, json=reqData)
                response.raise_for_status()
                json_response = response.json()
                
                if json_response['code'] == 0 and json_response['idList']:
                    company_id = str(json_response['idList'][0])
                    print(f"Found Company ID: {company_id}")
                    
                    # Get company information
                    company_info = get_company_info(company_id)
                    if company_info:
                        company_info_dict[company_name] = company_info
                        print("Successfully retrieved company information")
                    else:
                        print(f"Could not retrieve information for {company_name}")
                else:
                    print(f"No company ID found for {company_name}")
                
            except Exception as e:
                print(f"Error processing {company_name}: {str(e)}")
                continue
            
            # Add a small delay to avoid hitting rate limits
            time.sleep(1)
        
        # Add new columns to the DataFrame
        if company_info_dict:
            print("\nAdding company information to Excel file...")
            # Add columns in specific order
            ordered_keys = [
                '1. 成立时间',
                '2. 是否上市',
                '3. 母公司',
                '4. 母公司是否上市',
                '5. 融资历史',
                '6. 行业属性',
                '7. 产品/公司介绍',
                '8. 创始人信息'
            ]
            
            # Add columns in the specified order
            for key in ordered_keys:
                df[key] = df['企业名称'].map(lambda x: company_info_dict.get(x, {}).get(key, None))
        
        # Save the updated Excel file
        output_file = input_file.replace('.xlsx', '_first10_with_info.xlsx')
        output_file = output_file.replace('data/input/', 'data/output/')
        print(f"\nSaving updated file to: {output_file}")
        df.to_excel(output_file, index=False)
        print("File processing completed successfully!")
        
    except Exception as e:
        print(f"Error processing Excel file: {str(e)}")

if __name__ == '__main__':
    input_file = "data/input/小巨人list copy.xlsx"
    process_xiaojuren_list(input_file)
