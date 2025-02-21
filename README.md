# LCP Manufacturing Companies Data ETL Pipeline

A comprehensive data extraction, transformation, and loading (ETL) pipeline for analyzing Chinese manufacturing companies. This project integrates data from multiple sources including Xiniu, Qichacha, and Metaso APIs to gather detailed company information.

## Features

- Company Information Extraction:
  - Basic company details (establishment date, listing status)
  - Industry classification and track name
  - Parent company information
  - Stock reform status
  - Funding history
  - Founder information

- Data Analysis:
  - Peer fund investment tracking
  - Multiple funding rounds analysis
  - Industry attribute classification
  - Deal list cross-referencing

## Requirements

- Python 3.x
- pandas
- requests
- openpyxl

## Setup

1. Clone the repository:
```bash
git clone [repository-url]
cd lcp-manufacturing-companies-data-etl-pipeline
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure API credentials:
Update the following variables in `xiniu_api_client.py`:
```python
accesskeyid = "your_access_key_id"
accesskeysecret = "your_access_key_secret"
```

## Usage

1. Place your input Excel file in the project directory
2. Run the main script:
```bash
python xiniu_api_client.py
```

## Input File Format

The input Excel file should contain the following columns:
- 示范企业名称 (Company Name)

## Output

The script generates an enriched Excel file with additional columns including:
- 成立时间 (Establishment Date)
- 是否上市 (Listed Status)
- 母公司 (Parent Company)
- 融资历史 (Funding History)
- 行业属性 (Industry Attributes)
- 赛道名称 (Track Name)
- And more...

## Security Notes

- API credentials should be stored securely and not committed to version control
- Excel files containing sensitive company data are excluded from git tracking

## License

[Add your license information here]
