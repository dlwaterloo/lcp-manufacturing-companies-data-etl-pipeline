import hashlib
import time
import requests
import json
import os
from dotenv import load_dotenv

class QichachaClient:
    def __init__(self, app_key, secret_key):
        self.app_key = app_key
        self.secret_key = secret_key
        self.base_url = "https://api.qichacha.com"
        
    def _generate_token(self, timespan):
        """Generate authentication token"""
        str_to_sign = self.app_key + timespan + self.secret_key
        return hashlib.md5(str_to_sign.encode('utf-8')).hexdigest().upper()
        
    def get_company_changes(self, search_key, page_index="1", page_size="10"):
        """
        Get company changes information
        
        Args:
            search_key (str): Company name, unified social credit code, or registration number
            page_index (str): Page number, default is 1
            page_size (str): Items per page, default is 10 (max 10)
            
        Returns:
            dict: API response
        """
        # Generate timespan (Unix timestamp)
        timespan = str(int(time.time()))
        
        # Generate token
        token = self._generate_token(timespan)
        
        # Prepare headers
        headers = {
            "Token": token,
            "Timespan": timespan
        }
        
        # Prepare parameters
        params = {
            "key": self.app_key,
            "searchKey": search_key,
            "pageIndex": page_index,
            "pageSize": page_size
        }
        
        # Make the request
        try:
            response = requests.get(
                f"{self.base_url}/ECIChange/GetList",
                headers=headers,
                params=params
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error making request: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"Error decoding response: {e}")
            return None

    def get_all_company_changes(self, search_key):
        """
        Get all pages of company changes information
        
        Args:
            search_key (str): Company name, unified social credit code, or registration number
            
        Returns:
            dict: Combined API response with all pages
        """
        # Get first page to get total records
        first_page = self.get_company_changes(search_key, "1", "10")
        if not first_page or first_page.get('Status') != "200":
            return first_page

        total_records = first_page['Paging']['TotalRecords']
        total_pages = (total_records + 9) // 10  # Round up division

        # If only one page, return first page result
        if total_pages <= 1:
            return first_page

        # Get remaining pages
        all_results = first_page['Result']
        for page in range(2, total_pages + 1):
            page_data = self.get_company_changes(search_key, str(page), "10")
            if page_data and page_data.get('Status') == "200":
                all_results.extend(page_data['Result'])
            else:
                print(f"Error getting page {page}")
                break

        # Update the first page response with all results
        first_page['Result'] = all_results
        first_page['Paging']['PageSize'] = len(all_results)
        return first_page

    def save_to_file(self, data, company_name):
        """
        Save API response to a single text file, overwriting any previous content
        
        Args:
            data (dict): API response data
            company_name (str): Name of the company
        """
        filename = "qichacha_api_results.txt"
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(f"{'='*50}\n")
                f.write(f"Company: {company_name}\n")
                f.write(f"Time: {timestamp}\n")
                f.write(f"Total Changes: {len(data['Result'])}\n")
                f.write(f"{'='*50}\n\n")
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.write("\n")
            print(f"\nResults saved to: {filename}")
        except Exception as e:
            print(f"Error saving to file: {e}")

def find_stock_reform_date(data):
    """
    Find the date when company changed to a stock company
    
    Args:
        data (dict): API response data
        
    Returns:
        str: Date of stock reform or None if not found
    """
    if not data or 'Result' not in data:
        return None
        
    for change in data['Result']:
        if change['ProjectName'] == "市场主体类型变更":
            before_list = change.get('BeforeList', [])
            after_list = change.get('AfterList', [])
            
            # Check if any item in before_list contains '股份'
            before_has_stock = any('股份' in item for item in before_list)
            # Check if any item in after_list contains '股份'
            after_has_stock = any('股份' in item for item in after_list)
            
            # If changed to stock company
            if not before_has_stock and after_has_stock:
                return change['ChangeDate']
    
    return None

def test_api():
    # Load environment variables
    load_dotenv()
    
    # Initialize client with credentials from environment variables
    app_key = os.getenv('QICHACHA_APP_KEY')
    secret_key = os.getenv('QICHACHA_SECRET_KEY')
    
    if not app_key or not secret_key:
        print("Error: QICHACHA_APP_KEY and QICHACHA_SECRET_KEY environment variables must be set")
        return
        
    client = QichachaClient(app_key=app_key, secret_key=secret_key)
    
    # Test with a company name
    test_company = "荣耀终端股份有限公司"
    print(f"\nTesting API with company: {test_company}")
    
    # Get all pages of results
    result = client.get_all_company_changes(test_company)
    
    if result:
        print(f"\nTotal changes found: {len(result['Result'])}")
        # Find stock reform date
        reform_date = find_stock_reform_date(result)
        if reform_date:
            print(f"\n股改时间: {reform_date}")
        else:
            print("\n未找到股改记录")
        # Save results to file
        client.save_to_file(result, test_company)
    else:
        print("Failed to get response from API")

if __name__ == "__main__":
    test_api()
