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
   - Copy `.env.template` to `.env`:
     ```bash
     cp .env.template .env
     ```
   - Edit `.env` and add your API credentials:
     ```
     XINIU_ACCESS_KEY_ID=your_access_key_id
     XINIU_ACCESS_KEY_SECRET=your_access_key_secret
     METASO_SECRET_KEY=your_metaso_secret_key
     ```
   Note: Never commit the `.env` file to version control.

## Project Structure

```
.
├── src/
│   ├── api_clients/      # API client implementations
│   │   ├── xiniu_api_client.py
│   │   └── qichacha_api_client.py
│   ├── utils/           # Utility functions and processing scripts
│   │   ├── check_excel_sheets.py
│   │   ├── check_output.py
│   │   ├── check_pf_list.py
│   │   └── process_xiaojuren.py
│   └── tests/          # Test files
│       ├── metaso_api_test.py
│       ├── stock_reform_api_test.py
│       └── test_metaso.py
├── data/
│   ├── input/         # Input Excel files
│   └── output/        # Generated output files
├── requirements.txt
└── README.md
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
