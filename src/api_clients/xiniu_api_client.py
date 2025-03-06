# coding=utf-8

import hashlib
import time
import requests
import json
import pandas as pd
import os
import dotenv
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Get API credentials from environment variables
accesskeyid = os.getenv('XINIU_ACCESS_KEY_ID')
if not accesskeyid:
    raise ValueError("XINIU_ACCESS_KEY_ID environment variable is not set")

accesskeysecret = os.getenv('XINIU_ACCESS_KEY_SECRET')
if not accesskeysecret:
    raise ValueError("XINIU_ACCESS_KEY_SECRET environment variable is not set")


def signature_handler(reqData):
   signature = []
   for key in reqData.keys():
       if key != 'payload':
           signature.append(key + reqData[key])
       else:
           for p in reqData["payload"]:
               if isinstance(reqData["payload"][p], list):
                   items = reqData["payload"][p]
                   signature.append(p + "[" + ", ".join(items) + "]")
               else:
                   signature.append(p + str(reqData["payload"][p]))
   signature.sort()
   signature = ''.join(signature)
   signature += accesskeysecret
   signature_hash = hashlib.sha1(signature.encode('utf-8')).hexdigest()
   return signature_hash


def convert_to_utf8(json_data):
   try:
       # 解析JSON字符串
       json_obj = json.loads(json_data)
       # 将Python对象转换为JSON格式的字符串，并指定ensure_ascii=False确保非ASCII字符以原样输出
       json_str = json.dumps(json_obj, ensure_ascii=False)


       return json_str


   except Exception as e:
       print(f"Failed to convert JSON to UTF-8: {e}")
       return None


def get_funding_history(company_id):
    """
    Get company funding history using the /company/funding/list_all_2 endpoint
    """
    baseurl = 'https://api.xiniudata.com/openapi/v2/company/funding/list_all_2'

    payload = {
        "companyId": int(company_id)
    }

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
        
        if json_response['code'] == 0:
            # Get only active funding records and sort by date
            funding_list = [f for f in json_response.get('list', []) if f.get('active') == 'Y']
            funding_list.sort(key=lambda x: x.get('fundingDate', ''), reverse=True)
            
            # Format each funding record
            formatted_list = []
            for funding in funding_list:
                amount = funding.get('investment', 0)
                currency = funding.get('currency', 'USD')
                amount_str = f"{amount:,} {currency}" if amount else "金额未披露"
                
                formatted_list.append({
                    '融资时间': funding.get('fundingDate', ''),
                    '融资轮次': funding.get('round', ''),
                    '融资金额': amount_str,
                    '投资方': funding.get('investors', '未披露'),
                    '新闻标题': funding.get('newsTitle', '')
                })
            
            return formatted_list
        else:
            print(f"Error getting funding history: {json_response.get('codeMessage', 'Unknown error')}")
            return None
            
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as err:
        print(f'Other error occurred: {err}')
    except json.JSONDecodeError as json_err:
        print(f'JSON decode error: {json_err}')
    return None


def get_industry_attributes(company_id):
    """
    Get detailed industry attributes using both primary and ordered tags
    """
    # Get primary industry tags
    primary_url = 'https://api.xiniudata.com/openapi/v2/company/tag/list_primary_tag'
    ordered_url = 'https://api.xiniudata.com/openapi/v2/company/tag/list_ordered'

    payload = {
        "companyId": int(company_id)
    }

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
        # Get primary tags
        primary_response = requests.post(primary_url, json=reqData)
        primary_response.raise_for_status()
        primary_json = primary_response.json()

        # Get ordered tags
        ordered_response = requests.post(ordered_url, json=reqData)
        ordered_response.raise_for_status()
        ordered_json = ordered_response.json()

        result = {
            '主要行业': {},
            '所有行业标签': []
        }

        # Process primary tags
        if primary_json['code'] == 0:
            data = primary_json.get('data', {})
            result['主要行业'] = {
                '一级行业': data.get('primary_tag1', ''),
                '二级行业': data.get('primary_tag2', ''),
                '其他标签': data.get('other_tags', [])
            }

        # Process ordered tags
        if ordered_json['code'] == 0:
            ordered_tags = ordered_json.get('list', [])
            result['所有行业标签'] = [
                {
                    '标签名': tag.get('name', ''),
                    '标签ID': tag.get('id', '')
                }
                for tag in ordered_tags
            ]

        return result

    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as err:
        print(f'Other error occurred: {err}')
    except json.JSONDecodeError as json_err:
        print(f'JSON decode error: {json_err}')
    return None


def get_founder_info(company_id):
    """
    Get founder information using the /company/list_member endpoint
    """
    baseurl = 'https://api.xiniudata.com/openapi/v2/company/list_member'

    payload = {
        "companyId": int(company_id)
    }

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
        
        if json_response['code'] == 0:
            # Get founder information
            founders = []
            for member in json_response.get('list', []):
                position = member.get('position', '')
                if position and any(title in position.lower() for title in ['ceo', '创始人', '总裁']):
                    founder = {
                        '姓名': member.get('name', ''),
                        '职位': position,
                        '简介': member.get('description', '')
                    }
                    founders.append(founder)
            
            return founders if founders else None
            
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as err:
        print(f'Other error occurred: {err}')
    except json.JSONDecodeError as json_err:
        print(f'JSON decode error: {json_err}')
    return None


def get_company_id(company_name):
    """
    Get company ID from company name using the Xiniu API
    """
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
        print(f"\nMaking API request for company: {company_name}")
        print(f"Request data: {json.dumps(reqData, ensure_ascii=False, indent=2)}")
        
        response = requests.post(baseurl, json=reqData)
        print(f"Response status code: {response.status_code}")
        
        response.raise_for_status()
        json_response = response.json()
        print(f"Response data: {json.dumps(json_response, ensure_ascii=False, indent=2)}")
        
        if json_response['code'] == 0 and json_response['idList']:
            return str(json_response['idList'][0])
        else:
            print(f"API returned code {json_response.get('code')} with message: {json_response.get('codeMessage', 'No message')}")
        
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {str(e)}")
    except requests.exceptions.RequestException as e:
        print(f"Request Error: {str(e)}")
    except json.JSONDecodeError as e:
        print(f"JSON Decode Error: {str(e)}")
        print(f"Raw response: {response.text}")
    except Exception as e:
        print(f"Unexpected Error: {str(e)}")
    
    return None


def get_company_info(company_id):
    """
    Get specific company information:
    1. 成立时间 (Establishment Date)
    2. 是否上市 (Listed Status)
    3. 母公司 (Parent Company)
    4. 母公司是否上市 (Parent Company Listed Status)
    5. 融资历史 (Funding History)
    6. 行业属性 (Industry)
    7. 产品/公司介绍 (Product/Company Description)
    8. 创始人信息 (Founder Information)
    """
    baseurl = 'https://api.xiniudata.com/openapi/v2/company/get_2'

    payload = {
        "companyId": int(company_id)
    }

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
        
        # Print full response for debugging
        print("Full company details response:")
        print(json.dumps(json_response, ensure_ascii=False, indent=4))
        
        # Extract only the requested information
        if json_response['code'] == 0 and 'companyVO' in json_response:
            data = json_response['companyVO']
            
            # Get funding history
            funding_history = get_funding_history(company_id)
            funding_info = funding_history if funding_history else data.get('round')

            # Get detailed industry attributes
            industry_info = get_industry_attributes(company_id)

            # Get founder information
            founder_info = get_founder_info(company_id)
            
            result = {
                '成立时间': data.get('establishDate'),
                '是否上市': data.get('round'),
                '母公司': None,  # Not available in current response
                '母公司是否上市': None,  # Not available in current response
                '融资历史': funding_info,
                '行业属性': {
                    '简介': data.get('brief'),
                    '详细行业信息': industry_info
                },
                '产品/公司介绍': data.get('description'),
                '创始人信息': founder_info
            }
            return dict(sorted(result.items()))
        else:
            print("No valid data found in response")
            return None
            
    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as err:
        print(f'Other error occurred: {err}')
    except json.JSONDecodeError as json_err:
        print(f'JSON decode error: {json_err}')
    return None


def query_metaso(company_name):
    """
    Query the Metaso API for company information and return structured data
    
    Args:
        company_name (str): Name of the company to query
    Returns:
        dict: Dictionary containing parent company name and listing status
    """
    url = "https://metaso.cn/api/open/search"
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "Connection": "keep-alive",
        "secret-key": "d97435d71e8e73f3b9d398cc894f95e4"
    }

    question = f"请严格以JSON格式回答以下问题：1. {company_name}的母公司的名称是什么？如果不确定或没有，请回答NULL。2. 该母公司是否上市？如果是，请回答'是'，如果不是，请回答'不是'，如果不确定，请回答NULL。请按照以下格式回答：{{\"母公司名称\": \"具体名称或NULL\", \"母公司是否上市\": \"是/不是/NULL\"}}"

    data = {
        "question": question,
        "lang": "zh"
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
        
        if response.status_code == 200:
            full_response = ""
            for line in response.iter_lines():
                if line:
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
            return {
                "母公司名称": "NULL",
                "母公司是否上市": "NULL"
            }
            
    except Exception as e:
        print(f"Error querying Metaso API: {e}")
        return {
            "母公司名称": "NULL",
            "母公司是否上市": "NULL"
        }


def query_stock_reform(company_name):
    """
    Query the Metaso API for company stock reform information and return structured data
    
    Args:
        company_name (str): Name of the company to query
    Returns:
        dict: Dictionary containing whether it's a joint-stock company and its stock reform time
    """
    url = "https://metaso.cn/api/open/search"
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "Connection": "keep-alive",
        "secret-key": "d97435d71e8e73f3b9d398cc894f95e4"
    }

    question = f"请严格以JSON格式回答以下问题：1. {company_name}是否是股份公司？如果是，请回答'是'，如果不是，请回答'不是'，如果不确定，请回答NULL。2. 如果是股份公司，其股改的时间是什么时候？如果不确定或没有，请回答NULL。请按照以下格式回答：{{\"是否是股份公司\": \"是/不是/NULL\", \"股改时间\": \"具体时间或NULL\"}}"

    data = {
        "question": question,
        "lang": "zh"
    }
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), stream=True)
        
        if response.status_code == 200:
            full_response = ""
            for line in response.iter_lines():
                if line:
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
            return {
                "是否是股份公司": "NULL",
                "股改时间": "NULL"
            }
            
    except Exception as e:
        print(f"Error querying Metaso API: {e}")
        return {
            "是否是股份公司": "NULL",
            "股改时间": "NULL"
        }


def load_peer_funds(file_path="data/input/pf_companies.json"):
    """
    Load the peer funds from the JSON file
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            peer_funds = set(json.load(f))
        print(f"Loaded {len(peer_funds)} peer funds")
        return peer_funds
    except Exception as e:
        print(f"Error loading peer funds list: {str(e)}")
        return set()

def load_deallog_companies(file_path="data/input/deallog_companies.json"):
    """
    Load company names from deallog companies JSON file
    Returns a set of company names for direct string matching
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            company_names = set(json.load(f))
        print(f"Loaded {len(company_names)} companies from deallog list")
        return company_names
    except Exception as e:
        print(f"Error loading deallog list: {str(e)}")
        return set()


def is_likely_english(text):
    """Check if text contains English characters"""
    return any(ord(c) < 128 for c in text)

def split_chinese_english(name):
    """
    Split a company name that might contain both Chinese and English parts
    Example: "京东方 (BOE)" -> ["京东方", "BOE"]
    But don't split location names like "展讯通信（上海）有限公司"
    """
    name = name.strip()
    
    # Split by parentheses
    for separator in ['(', '（', '[', '【']:
        if separator in name:
            # Split and clean each part
            chinese_part = name.split(separator)[0].strip()
            eng_part = name.split(separator)[1].split(')')[0].split('）')[0].split(']')[0].split('】')[0].strip()
            
            # Only split if the part in parentheses looks like English
            if is_likely_english(eng_part):
                parts = []
                if chinese_part:
                    parts.append(chinese_part)
                if eng_part:
                    parts.append(eng_part)
                return parts
    
    # If no English part found, return the original name
    return [name]

def check_in_deallog(company_name, deallog_names):
    """
    Check if any part (Chinese or English) from the deallog list is included in the company name
    """
    if not company_name:
        return "不是"
    
    # Clean the company name
    company_name = company_name.strip()
    
    # Get all parts of the company name
    company_parts = split_chinese_english(company_name)
    print(f"\nChecking company: {company_name}")
    print(f"Company parts: {company_parts}")
    
    # Check if any deallog name part is included in any of the company name parts
    for deallog_name in deallog_names:
        deallog_parts = split_chinese_english(deallog_name)
        for deallog_part in deallog_parts:
            # Skip very short parts (like city names)
            if len(deallog_part) <= 2:
                continue
                
            for company_part in company_parts:
                if deallog_part in company_part:
                    print(f"Match found! Deallog part '{deallog_part}' is in company part '{company_part}'")
                    return "是"
                # Also check if company part is in deallog name (reverse check)
                if len(company_part) > 2 and company_part in deallog_part:
                    print(f"Match found! Company part '{company_part}' is in deallog part '{deallog_part}'")
                    return "是"
    
    return "不是"


def find_peer_fund_intersection(funding_history, peer_funds):
    """
    Find intersection between company's investors and peer funds
    """
    if not funding_history or not isinstance(funding_history, list):
        return "NULL"
    
    matched_funds = set()
    
    for funding in funding_history:
        investors = funding.get('投资方', '')
        if investors:
            # Split investors string into individual investors
            investor_list = [inv.strip() for inv in investors.split('，')]
            # Find intersection with peer funds
            matched_funds.update(set(investor_list) & peer_funds)
    
    return "，".join(sorted(matched_funds)) if matched_funds else "NULL"


def check_multiple_fundings_in_year(funding_history):
    """
    Check if there are more than 2 fundings in any year
    """
    if not funding_history or not isinstance(funding_history, list):
        return "不是"
    
    # Group fundings by year
    year_count = {}
    for funding in funding_history:
        funding_date = funding.get('融资时间', '')
        if funding_date:
            year = funding_date.split('/')[0]
            year_count[year] = year_count.get(year, 0) + 1
    
    # Check if any year has more than 2 fundings
    for count in year_count.values():
        if count > 2:
            return "是"
    return "不是"


def check_multiple_investors_in_round(funding_history):
    """
    Check if any round has more than 3 investors
    """
    if not funding_history or not isinstance(funding_history, list):
        return "不是"
    
    for funding in funding_history:
        investors = funding.get('投资方', '')
        if investors:
            # Split investors string into individual investors
            investor_list = [inv.strip() for inv in investors.split('，')]
            if len(investor_list) > 3:
                return "是"
    return "不是"


def check_multiple_peer_funds(funding_history, peer_funds):
    """
    Check if more than 2 peer funds have invested
    """
    if not funding_history or not isinstance(funding_history, list):
        return "不是"
    
    all_investors = set()
    for funding in funding_history:
        investors = funding.get('投资方', '')
        if investors:
            # Split investors string into individual investors
            investor_list = [inv.strip() for inv in investors.split('，')]
            all_investors.update(investor_list)
    
    # Find intersection with peer funds
    matched_funds = all_investors & peer_funds
    return "是" if len(matched_funds) >= 2 else "不是"


def process_excel_file(input_file):
    """
    Process Excel file and add company information columns, maintaining batch order
    """
    print(f"Reading Excel file: {input_file}")
    
    try:
        # Ensure input file exists
        if not os.path.exists(input_file):
            print(f"Error: Input file {input_file} not found")
            return
            
        # Create output file path
        output_file = input_file.replace('.xlsx', '_with_info.xlsx')
        if 'data/input/' in input_file:
            output_file = output_file.replace('data/input/', 'data/output/')
        else:
            output_file = os.path.join('data/output', os.path.basename(output_file))
            
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        
        # Load peer funds
        print("Loading peer funds list...")
        peer_funds = load_peer_funds()
        print(f"Loaded {len(peer_funds)} peer funds")
        
        # Load deallog companies
        print("\nLoading deallog companies list...")
        deallog_companies = load_deallog_companies()
        
        # Create Excel writer for output
        writer = pd.ExcelWriter(output_file, engine='openpyxl')
        
        # Read all sheets
        excel_file = pd.ExcelFile(input_file)
        sheet_names = excel_file.sheet_names
        
        # Process each sheet in order
        for sheet_name in sheet_names:
            print(f"\nProcessing sheet: {sheet_name}")
            
            # Read the sheet
            df = pd.read_excel(input_file, sheet_name=sheet_name)
            company_count = len(df)
            print(f"Found {company_count} companies to process in {sheet_name}")
            
            # Initialize new columns for company information
            df['成立时间'] = ''
            df['是否上市'] = ''
            df['母公司'] = ''
            df['母公司是否上市'] = ''
            df['融资历史'] = ''
            df['Peer Fund'] = ''
            df['某一年融资超2次'] = ''
            df['单轮3家以上fund'] = ''
            df['2家以上Peer Fund'] = ''
            df['已在Deal List'] = ''  
            df['行业属性'] = ''
            df['赛道名称'] = ''  # Add new column right after 行业属性
            df['产品/公司介绍'] = ''
            df['创始人信息'] = ''
            df['是否是股份公司'] = ''
            df['股改时间'] = ''
            
            # Process each company in the sheet
            for idx, row in df.iterrows():
                company_name = row['示范企业名称']
                print(f"\nProcessing company {idx+1}/{company_count} in {sheet_name}: {company_name}")
                
                # Check if company is in deallog list
                df.at[idx, '已在Deal List'] = check_in_deallog(company_name, deallog_companies)
                
                # Get company ID
                company_id = get_company_id(company_name)
                
                if company_id:
                    print(f"Found Company ID: {company_id}")
                    
                    # Get company information
                    company_info = get_company_info(company_id)
                    
                    if company_info:
                        # Update DataFrame with company information
                        df.at[idx, '成立时间'] = company_info.get('成立时间', '')
                        df.at[idx, '是否上市'] = company_info.get('是否上市', '')
                        
                        # Get funding history
                        funding_history = company_info.get('融资历史', [])
                        df.at[idx, '融资历史'] = funding_history
                        
                        # Find peer fund intersection
                        df.at[idx, 'Peer Fund'] = find_peer_fund_intersection(funding_history, peer_funds)
                        
                        # Add new funding analysis columns
                        df.at[idx, '某一年融资超2次'] = check_multiple_fundings_in_year(funding_history)
                        df.at[idx, '单轮3家以上fund'] = check_multiple_investors_in_round(funding_history)
                        df.at[idx, '2家以上Peer Fund'] = check_multiple_peer_funds(funding_history, peer_funds)
                        
                        # Get industry attributes and extract first tag name
                        industry_info = company_info.get('行业属性', {})
                        df.at[idx, '行业属性'] = industry_info
                        
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
                        df.at[idx, '创始人信息'] = company_info.get('创始人信息', '')
                        
                        # Query Metaso API for parent company information
                        print("Querying Metaso API for parent company information...")
                        metaso_info = query_metaso(company_name)
                        df.at[idx, '母公司'] = metaso_info.get('母公司名称', 'NULL')
                        df.at[idx, '母公司是否上市'] = metaso_info.get('母公司是否上市', 'NULL')
                        
                        # Query Metaso API for stock reform information
                        print("Querying Metaso API for stock reform information...")
                        stock_info = query_stock_reform(company_name)
                        df.at[idx, '是否是股份公司'] = stock_info.get('是否是股份公司', 'NULL')
                        df.at[idx, '股改时间'] = stock_info.get('股改时间', 'NULL')
                        
                        print("Successfully retrieved company information")
                    else:
                        print("Failed to retrieve company information")
                else:
                    print(f"No company ID found for {company_name}")
            
            # Reorder columns to put 赛道名称 after 行业属性
            cols = df.columns.tolist()
            industry_idx = cols.index('行业属性')
            track_idx = cols.index('赛道名称')
            cols.pop(track_idx)
            cols.insert(industry_idx + 1, '赛道名称')
            df = df[cols]
            
            # Save to Excel
            df.to_excel(writer, sheet_name=sheet_name, index=False)
        
        # Save and close the Excel writer
        writer.close()
        print(f"\nProcessed Excel file saved as: {output_file}")
        
    except Exception as e:
        print(f"Error processing Excel file: {str(e)}")
        raise


def test_first_10_rows():
    """
    Test the script with first 10 rows of the first sheet
    """
    try:
        # Load peer funds and deallog companies
        peer_funds = load_peer_funds()
        deallog_companies = load_deallog_companies()
        
        print("\nProcessing first 10 rows...")
        
        # Read the first sheet
        input_file = "data/input/1-6批制造业单项冠军 copy.xlsx"
        output_file = input_file.replace('.xlsx', '_first10_with_info.xlsx')
        output_file = output_file.replace('data/input/', 'data/output/')
        
        # Create Excel writer
        os.makedirs(os.path.dirname(output_file), exist_ok=True)  # Ensure output directory exists
        writer = pd.ExcelWriter(output_file, engine='openpyxl')
        
        # Read first sheet
        df = pd.read_excel(input_file, sheet_name="第一批")
        
        # Take first 10 rows
        df = df.head(10)
        company_count = len(df)
        print(f"\nProcessing first {company_count} companies from 第一批")
        
        # Initialize new columns for company information
        df['成立时间'] = ''
        df['是否上市'] = ''
        df['母公司'] = ''
        df['母公司是否上市'] = ''
        df['融资历史'] = ''
        df['Peer Fund'] = ''
        df['某一年融资超2次'] = ''
        df['单轮3家以上fund'] = ''
        df['2家以上Peer Fund'] = ''
        df['已在Deal List'] = ''  
        df['行业属性'] = ''
        df['赛道名称'] = ''  # Add new column right after 行业属性
        df['产品/公司介绍'] = ''
        df['创始人信息'] = ''
        df['是否是股份公司'] = ''
        df['股改时间'] = ''
        
        # Process each company
        for idx, row in df.iterrows():
            company_name = row['示范企业名称']
            print(f"\nProcessing company {idx+1}/{company_count}: {company_name}")
            
            # Check if company is in deallog list
            df.at[idx, '已在Deal List'] = check_in_deallog(company_name, deallog_companies)
            
            # Get company ID
            company_id = get_company_id(company_name)
            
            if company_id:
                print(f"Found Company ID: {company_id}")
                
                # Get company information
                company_info = get_company_info(company_id)
                
                if company_info:
                    # Update DataFrame with company information
                    df.at[idx, '成立时间'] = company_info.get('成立时间', '')
                    df.at[idx, '是否上市'] = company_info.get('是否上市', '')
                    
                    # Get funding history
                    funding_history = company_info.get('融资历史', [])
                    df.at[idx, '融资历史'] = funding_history
                    
                    # Find peer fund intersection
                    df.at[idx, 'Peer Fund'] = find_peer_fund_intersection(funding_history, peer_funds)
                    
                    # Add new funding analysis columns
                    df.at[idx, '某一年融资超2次'] = check_multiple_fundings_in_year(funding_history)
                    df.at[idx, '单轮3家以上fund'] = check_multiple_investors_in_round(funding_history)
                    df.at[idx, '2家以上Peer Fund'] = check_multiple_peer_funds(funding_history, peer_funds)
                    
                    df.at[idx, '行业属性'] = company_info.get('行业属性', '')
                    df.at[idx, '赛道名称'] = ''  # Add new column right after 行业属性
                    df.at[idx, '产品/公司介绍'] = company_info.get('产品/公司介绍', '')
                    df.at[idx, '创始人信息'] = company_info.get('创始人信息', '')
                    
                    # Get industry attributes and extract first tag name
                    industry_info = company_info.get('行业属性', {})
                    df.at[idx, '行业属性'] = industry_info
                    
                    # Extract first tag name from 所有行业标签
                    if isinstance(industry_info, dict) and '详细行业信息' in industry_info:
                        detailed_info = industry_info['详细行业信息']
                        if isinstance(detailed_info, dict) and '所有行业标签' in detailed_info:
                            all_tags = detailed_info['所有行业标签']
                            if all_tags and isinstance(all_tags, list) and len(all_tags) > 0:
                                first_tag = all_tags[0]
                                if isinstance(first_tag, dict) and '标签名' in first_tag:
                                    df.at[idx, '赛道名称'] = first_tag['标签名']
                    
                    # Query Metaso API for parent company information
                    print("Querying Metaso API for parent company information...")
                    metaso_info = query_metaso(company_name)
                    df.at[idx, '母公司'] = metaso_info.get('母公司名称', 'NULL')
                    df.at[idx, '母公司是否上市'] = metaso_info.get('母公司是否上市', 'NULL')
                    
                    # Query Metaso API for stock reform information
                    print("Querying Metaso API for stock reform information...")
                    stock_info = query_stock_reform(company_name)
                    df.at[idx, '是否是股份公司'] = stock_info.get('是否是股份公司', 'NULL')
                    df.at[idx, '股改时间'] = stock_info.get('股改时间', 'NULL')
                    
                    print("Successfully retrieved company information")
                else:
                    print("Failed to retrieve company information")
            else:
                print(f"No company ID found for {company_name}")
        
        # Save to Excel with the sheet name
        df.to_excel(writer, sheet_name='第一批', index=False)
        writer.close()
        
        print("\nTest completed successfully!")
        
        # Print summary of the results
        print("\nResults Summary:")
        print(f"Companies processed: {company_count}")
        print("\nFunding Analysis:")
        print(f"某一年融资超2次: {dict(df['某一年融资超2次'].value_counts())}")
        print(f"单轮3家以上fund: {dict(df['单轮3家以上fund'].value_counts())}")
        print(f"2家以上Peer Fund: {dict(df['2家以上Peer Fund'].value_counts())}")
        
    except Exception as e:
        print(f"Error in test: {str(e)}")
        import traceback
        print(traceback.format_exc())


def test_api():
    # Process Excel file
    excel_file = "data/input/1-6批制造业单项冠军 copy.xlsx"
    process_excel_file(excel_file)

def test_specific_companies():
    """Test specific companies against the deallog list"""
    print("Loading peer funds list...")
    peer_funds = load_peer_funds()
    print(f"Loaded {len(peer_funds)} peer funds")
    
    print("\nLoading deallog companies list...")
    deallog_companies = load_deallog_companies()
    
    # Test cases
    test_companies = [
        "展讯通信（上海）有限公司",  # Company with location
        "京东方科技 (BOE Technology)",  # Company with English name
        "中芯国际（SMIC）",  # Company with English abbreviation
        "阿里巴巴(Alibaba)",  # Another company with English name
    ]
    
    for company_name in test_companies:
        result = check_in_deallog(company_name, deallog_companies)
        print(f"\nFinal result for {company_name}: {result}")
        print("-" * 50)

def get_company_industry(company_id):
    """
    Get company industry information using the /company/industry/list endpoint
    """
    baseurl = 'https://api.xiniudata.com/openapi/v2/company/industry/list'

    payload = {
        "companyId": int(company_id)
    }

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
        
        if json_response['code'] == 0:
            print("\n赛道名称:")
            for industry in json_response['list']:
                print(f"- {industry['name']}")
            return json_response
        
    except Exception as e:
        print(f"Error: {str(e)}")
    
    return None

def test_industry_api():
    """Test the industry list API with a known company ID"""
    # Test with BOE (京东方)
    company_id = 93819
    get_company_industry(company_id)

if __name__ == '__main__':
    test_first_10_rows()
