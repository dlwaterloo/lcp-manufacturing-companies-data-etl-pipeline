import requests
import json

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

    # Structured question to get clear, specific answers
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
            
            print(full_response)
            
        else:
            print(json.dumps({
                "是否是股份公司": "NULL",
                "股改时间": "NULL"
            }, ensure_ascii=False))
            
    except Exception as e:
        print(json.dumps({
            "是否是股份公司": "NULL",
            "股改时间": "NULL"
        }, ensure_ascii=False))

def test_single_company():
    """
    Test the Metaso API for a single company
    """
    company = "京东方科技集团股份有限公司"
    query_stock_reform(company)

if __name__ == "__main__":
    test_single_company()
