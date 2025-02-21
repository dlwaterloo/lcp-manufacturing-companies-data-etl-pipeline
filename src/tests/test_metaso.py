import sys
import os
import requests
import json
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Load environment variables
load_dotenv()

from src.api_clients.xiniu_api_client import query_metaso, query_stock_reform

def test_metaso_api():
    """
    Test the Metaso API with detailed error reporting
    """
    url = "https://metaso.cn/api/open/search"
    headers = {
        "Content-Type": "application/json",
        "Accept": "text/event-stream",
        "Connection": "keep-alive",
        "secret-key": os.getenv('METASO_SECRET_KEY', 'd97435d71e8e73f3b9d398cc894f95e4')  # Using default for backward compatibility
    }

    company_name = "京东方科技集团股份有限公司"
    question = f"请严格以JSON格式回答以下问题：1. {company_name}的母公司的名称是什么？如果不确定或没有，请回答NULL。2. 该母公司是否上市？如果是，请回答'是'，如果不是，请回答'不是'，如果不确定，请回答NULL。请按照以下格式回答：{{\"母公司名称\": \"具体名称或NULL\", \"母公司是否上市\": \"是/不是/NULL\"}}"

    data = {
        "question": question,
        "lang": "zh"
    }
    
    print("Testing Metaso API...")
    print(f"URL: {url}")
    print(f"Headers: {json.dumps(headers, indent=2)}")
    print(f"Data: {json.dumps(data, indent=2)}")
    
    try:
        print("\nSending request...")
        response = requests.post(url, headers=headers, json=data, stream=True)
        
        print(f"\nResponse Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("\nProcessing response stream...")
            full_response = ""
            for line in response.iter_lines():
                if line:
                    decoded_line = line.decode('utf-8')
                    print(f"Raw line: {decoded_line}")
                    if decoded_line.startswith("data:") and not decoded_line.startswith("data:[DONE]"):
                        try:
                            json_str = decoded_line[5:]  # Remove "data:" prefix
                            print(f"JSON string: {json_str}")
                            data = json.loads(json_str)
                            if data.get("type") == "append-text":
                                full_response += data.get("text", "")
                        except json.JSONDecodeError as e:
                            print(f"JSON decode error: {e}")
                            continue
            
            print(f"\nFull Response: {full_response}")
            
        else:
            print(f"\nError Response Content: {response.text}")
            
    except Exception as e:
        print(f"\nException occurred: {str(e)}")
        import traceback
        print(traceback.format_exc())

if __name__ == "__main__":
    test_metaso_api()
