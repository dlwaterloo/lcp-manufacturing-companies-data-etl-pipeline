#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Run the ETL process for the top 5 rows of each sheet in the 小巨人list copy.xlsx file
without using the Metaso API with formatted funding history
"""

import os
import sys
import importlib.util
import pandas as pd
from openpyxl.styles import Alignment, Border, Side
import json
import requests
import asyncio
import aiohttp
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
import time

# Set up Jinja2 environment
template_env = Environment(loader=FileSystemLoader('src/templates'))

# Import the xiniu_api_client module
spec = importlib.util.spec_from_file_location("xiniu_api_client", 
                                             "src/api_clients/xiniu_api_client.py")
xiniu_api_client = importlib.util.module_from_spec(spec)
spec.loader.exec_module(xiniu_api_client)

async def query_metaso_async(company_name, session):
    """
    Query the Metaso API for company information and return structured data
    
    Args:
        company_name (str): Name of the company to query
        session (aiohttp.ClientSession): Async HTTP session
    Returns:
        dict: Dictionary containing parent company name and listing status
    """
    url = "https://metaso.cn/api/open/search"
    
    # Get API key from environment variable
    metaso_key = os.getenv('METASO_SECRET_KEY')
    if not metaso_key:
        raise ValueError("METASO_SECRET_KEY environment variable is not set")
        
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "Connection": "keep-alive",
        "secret-key": metaso_key
    }

    try:
        # Load and render template
        template = template_env.get_template('parent_company_prompt.j2')
        question = template.render(company_name=company_name)
        
        data = {
            "question": question,
            "lang": "zh"
        }
        
        # Make async API call
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                full_response = ""
                # Read the response as a stream
                async for line in response.content:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data:") and not decoded_line.startswith("data:[DONE]"):
                        try:
                            json_str = decoded_line[5:]  # Remove "data:" prefix
                            data = json.loads(json_str)
                            if data.get("type") == "append-text":
                                full_response += data.get("text", "")
                        except json.JSONDecodeError:
                            continue
                
                try:
                    # Clean up the response string to ensure it's valid JSON
                    full_response = full_response.strip()
                    if full_response.startswith('```json'):
                        full_response = full_response[7:]  # Remove ```json
                    if full_response.endswith('```'):
                        full_response = full_response[:-3]  # Remove ```
                    full_response = full_response.strip()
                    
                    # Parse the JSON response
                    result = json.loads(full_response)
                    return result
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON response: {e}")
                    print(f"Raw response: {full_response}")
                    return {
                        "母公司名称": "NULL",
                        "母公司是否上市": "NULL"
                    }
            else:
                print(f"Metaso API request failed for {company_name} with status {response.status}")
                return {
                    "母公司名称": "NULL",
                    "母公司是否上市": "NULL"
                }
    except Exception as e:
        print(f"Error querying Metaso API for {company_name}: {e}")
        return {
            "母公司名称": "NULL",
            "母公司是否上市": "NULL"
        }

async def query_stock_reform_async(company_name, session):
    """
    Query the Metaso API for company stock reform information and return structured data
    
    Args:
        company_name (str): Name of the company to query
        session (aiohttp.ClientSession): Async HTTP session
    Returns:
        dict: Dictionary containing whether it's a joint-stock company and its stock reform time
    """
    url = "https://metaso.cn/api/open/search"
    
    # Get API key from environment variable
    metaso_key = os.getenv('METASO_SECRET_KEY')
    if not metaso_key:
        raise ValueError("METASO_SECRET_KEY environment variable is not set")
        
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "Connection": "keep-alive",
        "secret-key": metaso_key
    }

    try:
        # Load and render template
        template = template_env.get_template('stock_reform_prompt.j2')
        question = template.render(company_name=company_name)
        
        data = {
            "question": question,
            "lang": "zh"
        }
        
        # Make async API call
        async with session.post(url, headers=headers, json=data) as response:
            if response.status == 200:
                full_response = ""
                # Read the response as a stream
                async for line in response.content:
                    decoded_line = line.decode('utf-8')
                    if decoded_line.startswith("data:") and not decoded_line.startswith("data:[DONE]"):
                        try:
                            json_str = decoded_line[5:]  # Remove "data:" prefix
                            data = json.loads(json_str)
                            if data.get("type") == "append-text":
                                full_response += data.get("text", "")
                        except json.JSONDecodeError:
                            continue
                
                try:
                    # Clean up the response string to ensure it's valid JSON
                    full_response = full_response.strip()
                    if full_response.startswith('```json'):
                        full_response = full_response[7:]  # Remove ```json
                    if full_response.endswith('```'):
                        full_response = full_response[:-3]  # Remove ```
                    full_response = full_response.strip()
                    
                    # Parse the JSON response
                    result = json.loads(full_response)
                    return result
                except json.JSONDecodeError as e:
                    print(f"Error parsing JSON response: {e}")
                    print(f"Raw response: {full_response}")
                    return {
                        "是否是股份公司": "NULL",
                        "股改时间": "NULL"
                    }
            else:
                print(f"Metaso API request failed for {company_name} with status {response.status}")
                return {
                    "是否是股份公司": "NULL",
                    "股改时间": "NULL"
                }
    except Exception as e:
        print(f"Error querying Metaso API for {company_name}: {e}")
        return {
            "是否是股份公司": "NULL",
            "股改时间": "NULL"
        }

async def get_xiniu_info_async(company_name):
    """
    Get company information from Xiniu API asynchronously
    
    Args:
        company_name (str): Name of the company
    Returns:
        tuple: (company_info, funding_history)
    """
    company_id = xiniu_api_client.get_company_id(company_name)
    
    # Try with modified name if parentheses are present and no ID was found
    if not company_id and '(' in company_name and ')' in company_name:
        # First try: Add spaces around parentheses
        modified_name = company_name.replace('(', ' (').replace(')', ') ')
        print(f"No match found. Trying with modified name: {modified_name}")
        company_id = xiniu_api_client.get_company_id(modified_name)
        
        # Second try: Remove content in parentheses if still no match
        if not company_id:
            start_idx = company_name.find('(')
            end_idx = company_name.find(')')
            if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
                simplified_name = company_name[:start_idx] + company_name[end_idx+1:]
                simplified_name = ' '.join(simplified_name.split())
                print(f"Still no match. Trying with simplified name: {simplified_name}")
                company_id = xiniu_api_client.get_company_id(simplified_name)
    
    if company_id:
        print(f"Found Company ID: {company_id}")
        company_info = xiniu_api_client.get_company_info(company_id)
        return company_info
    else:
        print(f"No company ID found for {company_name}")
        return None

async def process_company_async(company_name, session):
    """
    Process a single company asynchronously, making all API calls in parallel
    """
    try:
        # Create all API tasks at once
        tasks = [
            get_xiniu_info_async(company_name),
            query_metaso_async(company_name, session),
            query_stock_reform_async(company_name, session)
        ]
        
        # Run all API calls in parallel
        company_info, parent_info, stock_info = await asyncio.gather(*tasks)
        return company_info, parent_info, stock_info
        
    except Exception as e:
        print(f"Error processing company {company_name}: {e}")
        return None, None, None

async def process_single_company(idx, company_name, session, df, peer_funds, deallog_companies):
    """
    Process a single company and update the DataFrame
    """
    try:
        # Check if company is in deallog list (this is fast, so we do it synchronously)
        df.at[idx, '已在Deal List'] = xiniu_api_client.check_in_deallog(company_name, deallog_companies)
        
        # Process company with parallel API calls
        company_info, parent_info, stock_info = await process_company_async(company_name, session)
        
        if company_info:
            # Update DataFrame with company information
            df.at[idx, '成立时间'] = company_info.get('成立时间', '')
            df.at[idx, '是否上市'] = company_info.get('是否上市', '')
            
            # Get funding history
            funding_history = company_info.get('融资历史', [])
            df.at[idx, '融资历史'] = format_funding_history(funding_history)
            
            # Find peer fund intersection
            df.at[idx, 'Peer Fund'] = xiniu_api_client.find_peer_fund_intersection(funding_history, peer_funds)
            
            # Add new funding analysis columns
            df.at[idx, '某一年融资超2次'] = xiniu_api_client.check_multiple_fundings_in_year(funding_history)
            df.at[idx, '单轮3家以上fund'] = xiniu_api_client.check_multiple_investors_in_round(funding_history)
            df.at[idx, '2家以上Peer Fund'] = xiniu_api_client.check_multiple_peer_funds(funding_history, peer_funds)
            
            # Get industry attributes and extract first tag name
            industry_info = company_info.get('行业属性', {})
            df.at[idx, '行业属性'] = format_industry_attributes(industry_info)
            
            # Extract first tag name from 所有行业标签
            if isinstance(industry_info, dict) and '详细行业信息' in industry_info:
                detailed_info = industry_info['详细行业信息']
                if isinstance(detailed_info, dict) and '所有行业标签' in detailed_info:
                    all_tags = detailed_info['所有行业标签']
                    if all_tags and isinstance(all_tags, list) and len(all_tags) > 0:
                        first_tag = all_tags[0]
                        if isinstance(first_tag, dict) and '标签名' in first_tag:
                            df.at[idx, '赛道名称'] = first_tag['标签名']
            
            df.at[idx, '产品/公司介绍'] = company_info.get('产品/公司介绍', '')
            df.at[idx, '创始人信息'] = format_founder_info(company_info.get('创始人信息', ''))
            
            # Validate parent company and stock reform information
            parent_info = validate_parent_company_response(parent_info)
            df.at[idx, '母公司'] = parent_info.get('母公司名称', 'NULL')
            df.at[idx, '母公司是否上市'] = parent_info.get('母公司是否上市', 'NULL')
            
            stock_info = validate_stock_reform_response(stock_info)
            df.at[idx, '是否是股份公司'] = stock_info.get('是否是股份公司', 'NULL')
            df.at[idx, '股改时间'] = stock_info.get('股改时间', 'NULL')
            
            print(f"Successfully processed company: {company_name}")
            return True
        else:
            print(f"Failed to process company: {company_name}")
            return False
            
    except Exception as e:
        print(f"Error processing company {company_name}: {e}")
        return False

async def process_sheet_async(sheet_name, df, peer_funds, deallog_companies, session):
    """
    Process a single sheet asynchronously, one row at a time
    """
    start_time = time.time()
    print(f"\nProcessing sheet: {sheet_name}")
    
    # Define row ranges for each sheet
    sheet_ranges = {
        '第一批': (238, 248),    # Rows 239-248 (0-based indexing)
        '第二批': (1694, 1744),  # Rows 1695-1744
        '第三批': (2881, 2931),  # Rows 2882-2931
        '第四批': (3500, 4357),  # Rows 3501-4357
        '第五批': (3500, 3671),  # Rows 3501-3671
        '第六批': (2962, 3012),  # Rows 2963-3012
    }
    
    if sheet_name not in sheet_ranges:
        print(f"Warning: No row range defined for sheet {sheet_name}")
        return sheet_name, df
        
    start_row, end_row = sheet_ranges[sheet_name]
    total_rows = end_row - start_row
    
    print(f"Processing rows {start_row+1}-{end_row} ({total_rows} companies) in {sheet_name}")
    
    # Initialize new columns in the original DataFrame if they don't exist
    new_columns = ['成立时间', '是否上市', '母公司', '母公司是否上市', '融资历史', 'Peer Fund',
                  '某一年融资超2次', '单轮3家以上fund', '2家以上Peer Fund', '已在Deal List',
                  '行业属性', '赛道名称', '产品/公司介绍', '创始人信息', '是否是股份公司', '股改时间']
    
    for col in new_columns:
        if col not in df.columns:
            df[col] = ''
    
    # Find company name column
    company_name_column = '示范企业名称' if '示范企业名称' in df.columns else '企业名称'
    if company_name_column not in df.columns:
        print(f"Warning: Could not find company name column in sheet {sheet_name}")
        # Try to find a column that might contain company names
        for col in df.columns:
            if '名称' in col or 'name' in col.lower() or '企业' in col:
                company_name_column = col
                print(f"Using column '{company_name_column}' for company names")
                break
        if company_name_column not in df.columns:
            print(f"Error: Could not find a suitable company name column in sheet {sheet_name}")
            return sheet_name, df
    
    # Process companies one by one
    successful = 0
    processed = 0
    for idx in range(start_row, end_row):  
        company_name = df.iloc[idx][company_name_column]
        current_row = idx + 1  # Convert to 1-based indexing for display
        current_count = processed + 1
        print(f"\nProcessing company {current_count}/{total_rows} (Row {current_row}): {company_name}")
        
        if await process_single_company(idx, company_name, session, df, peer_funds, deallog_companies):
            successful += 1
        processed += 1
        
        # Print progress
        elapsed_time = time.time() - start_time
        avg_time_per_company = elapsed_time / processed
        remaining = total_rows - processed
        estimated_remaining = remaining * avg_time_per_company
        
        print(f"\nProgress update:")
        print(f"Processed: {processed}/{total_rows} companies ({processed/total_rows*100:.1f}%)")
        print(f"Successfully processed: {successful} companies")
        print(f"Average time per company: {avg_time_per_company:.2f} seconds")
        print(f"Estimated time remaining: {estimated_remaining/60:.1f} minutes")
    
    # Reorder columns to put 赛道名称 after 行业属性
    cols = df.columns.tolist()
    industry_idx = cols.index('行业属性')
    track_idx = cols.index('赛道名称')
    cols.pop(track_idx)
    cols.insert(industry_idx + 1, '赛道名称')
    df = df[cols]
    
    end_time = time.time()
    duration = end_time - start_time
    print(f"\nFinished processing rows {start_row+1}-{end_row} in sheet {sheet_name} in {duration/60:.1f} minutes")
    print(f"Successfully processed {successful}/{total_rows} companies")
    return sheet_name, df

async def process_without_metaso(input_file):
    """
    Process the top 20 rows of each sheet in the input file without using Metaso API
    """
    start_time = time.time()
    print(f"Reading Excel file: {input_file}")
    
    # Load peer funds and deallog companies
    peer_funds = xiniu_api_client.load_peer_funds()
    deallog_companies = xiniu_api_client.load_deallog_companies()
    
    # Read all sheets
    excel_file = pd.ExcelFile(input_file)
    sheet_names = excel_file.sheet_names
    
    # Create tasks for processing each sheet
    tasks = []
    async with aiohttp.ClientSession() as session:
        for sheet_name in sheet_names:
            # Read the sheet
            df = pd.read_excel(input_file, sheet_name=sheet_name)
            tasks.append(process_sheet_async(sheet_name, df, peer_funds, deallog_companies, session))
        
        # Process all sheets in parallel
        results = await asyncio.gather(*tasks)
    
    # Create output file path in the output directory
    output_dir = os.path.join(os.path.dirname(os.path.dirname(input_file)), 'output')
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, os.path.basename(input_file).replace('.xlsx', '_formatted.xlsx'))
    
    # Create Excel writer for output
    writer = pd.ExcelWriter(output_file, engine='openpyxl')
    
    # Save all processed sheets
    for sheet_name, df in results:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Get the worksheet
        worksheet = writer.sheets[sheet_name]
        
        # Format the cells
        for row in worksheet.iter_rows():
            for cell in row:
                cell.alignment = Alignment(wrap_text=True, vertical='top')
                cell.border = Border(
                    left=Side(style='thin'),
                    right=Side(style='thin'),
                    top=Side(style='thin'),
                    bottom=Side(style='thin')
                )
        
        # Adjust column widths
        for column in worksheet.columns:
            max_length = 0
            column = list(column)
            for cell in column:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            worksheet.column_dimensions[column[0].column_letter].width = min(adjusted_width, 50)
    
    # Save the Excel file
    writer.close()
    end_time = time.time()
    duration = end_time - start_time
    print(f"\nProcessed file saved as: {output_file}")
    print(f"Total processing time: {duration/60:.1f} minutes")

def validate_parent_company_response(response):
    """
    Validate the parent company response format and values
    
    Args:
        response (dict): Response from Metaso API
    Returns:
        dict: Validated response with correct format
    """
    valid_status = ["是", "不是", "NULL"]
    default_response = {
        "母公司名称": "NULL",
        "母公司是否上市": "NULL"
    }
    
    try:
        # Check if all required fields exist
        if not all(key in response for key in default_response.keys()):
            print("Missing required fields in parent company response")
            return default_response
            
        # Validate parent company name
        if not response["母公司名称"] or not isinstance(response["母公司名称"], str):
            response["母公司名称"] = "NULL"
            
        # If parent company is NULL, listing status must also be NULL
        if response["母公司名称"] == "NULL":
            response["母公司是否上市"] = "NULL"
        # Otherwise validate listing status
        elif response["母公司是否上市"] not in valid_status:
            print(f"Invalid listing status: {response['母公司是否上市']}")
            response["母公司是否上市"] = "NULL"
            
        return response
    except Exception as e:
        print(f"Error validating parent company response: {e}")
        return default_response

def validate_stock_reform_response(response):
    """
    Validate the stock reform response format and values
    
    Args:
        response (dict): Response from Metaso API
    Returns:
        dict: Validated response with correct format
    """
    valid_status = ["是", "不是", "NULL"]
    default_response = {
        "是否是股份公司": "NULL",
        "股改时间": "NULL"
    }
    
    try:
        # Check if all required fields exist
        if not all(key in response for key in default_response.keys()):
            print("Missing required fields in stock reform response")
            return default_response
            
        # Validate company status
        if response["是否是股份公司"] not in valid_status:
            print(f"Invalid company status: {response['是否是股份公司']}")
            response["是否是股份公司"] = "NULL"
            
        # Validate reform date format if present
        if response["股改时间"] != "NULL":
            try:
                # Try to parse the date
                datetime.strptime(response["股改时间"], "%Y-%m-%d")
            except ValueError:
                print(f"Invalid date format: {response['股改时间']}")
                response["股改时间"] = "NULL"
                
        return response
    except Exception as e:
        print(f"Error validating stock reform response: {e}")
        return default_response

def format_funding_history(funding_history):
    """
    Format funding history in a structured way with time, round, amount, and investors
    """
    if not funding_history or not isinstance(funding_history, list) or len(funding_history) == 0:
        return "未融资"
    
    formatted_entries = []
    for entry in funding_history:
        time = entry.get('融资时间', '')
        round_name = entry.get('融资轮次', '')
        amount = entry.get('融资金额', '')
        investors = entry.get('投资方', '')
        
        formatted_entry = f"{time}, {round_name}, {amount}, {investors}"
        formatted_entries.append(formatted_entry)
    
    return "\n".join(formatted_entries)

def format_dict_to_string(data):
    """
    Format dictionary data to string, removing brackets
    """
    if not data:
        return ""
    
    if isinstance(data, dict):
        return str(data).replace("{", "").replace("}", "").replace("[", "").replace("]", "")
    
    if isinstance(data, list):
        return str(data).replace("[", "").replace("]", "")
    
    return str(data)

def format_industry_attributes(industry_info):
    """
    Format industry attributes, removing brackets and putting each attribute on a different line
    """
    if not industry_info:
        return ""
    
    # If it's already a string, just return it
    if isinstance(industry_info, str):
        return industry_info.replace("[", "").replace("]", "").replace("{", "").replace("}", "")
    
    # If it's a dictionary
    if isinstance(industry_info, dict):
        formatted_items = []
        for k, v in industry_info.items():
            if isinstance(v, (dict, list)):
                # Skip nested structures that will be handled separately
                continue
            formatted_items.append(f"{k}: {v}")
        
        # Handle detailed industry info separately if it exists
        if '详细行业信息' in industry_info and isinstance(industry_info['详细行业信息'], dict):
            detailed_info = industry_info['详细行业信息']
            for k, v in detailed_info.items():
                if k == '所有行业标签' and isinstance(v, list):
                    # Format tags
                    for tag in v:
                        if isinstance(tag, dict) and '标签名' in tag:
                            formatted_items.append(f"标签: {tag['标签名']}")
                elif not isinstance(v, (dict, list)):
                    formatted_items.append(f"{k}: {v}")
        
        return "\n".join(formatted_items)
    
    # If it's a list
    if isinstance(industry_info, list):
        formatted_items = []
        for item in industry_info:
            if isinstance(item, dict):
                for k, v in item.items():
                    formatted_items.append(f"{k}: {v}")
            else:
                formatted_items.append(str(item))
        
        return "\n".join(formatted_items)
    
    return str(industry_info)

def format_founder_info(founder_info):
    """
    Format founder information, removing brackets and putting each person on a different line
    """
    if not founder_info:
        return ""
    
    # If it's already a string, just return it
    if isinstance(founder_info, str):
        return founder_info.replace("[", "").replace("]", "").replace("{", "").replace("}", "")
    
    # If it's a list of founders
    if isinstance(founder_info, list):
        formatted_founders = []
        for founder in founder_info:
            if isinstance(founder, dict):
                # Convert each founder dict to a string without brackets
                founder_str = ", ".join([f"{k}: {v}" for k, v in founder.items()])
                formatted_founders.append(founder_str)
            else:
                formatted_founders.append(str(founder).replace("[", "").replace("]", "").replace("{", "").replace("}", ""))
        
        return "\n".join(formatted_founders)
    
    # If it's a dictionary
    if isinstance(founder_info, dict):
        return str(founder_info).replace("{", "").replace("}", "").replace("[", "").replace("]", "")
    
    return str(founder_info)

def main():
    """
    Process the top 20 rows of each sheet in the 小巨人list copy.xlsx file without using Metaso API
    with formatted funding history
    """
    input_file = "data/input/小巨人list copy.xlsx"
    
    print(f"Processing top 20 rows of file: {input_file}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    asyncio.run(process_without_metaso(input_file))

if __name__ == "__main__":
    main()
