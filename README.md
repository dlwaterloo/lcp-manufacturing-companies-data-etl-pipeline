# LCP Manufacturing Companies Data ETL Pipeline

A comprehensive data extraction, transformation, and loading (ETL) pipeline for analyzing Chinese manufacturing companies. This project integrates data from multiple sources including Xiniu and Metaso APIs to gather detailed company information, with high-performance parallel processing capabilities.

## Features

- High Performance Data Processing:
  - Parallel processing of 500 companies per sheet
  - Batch processing with 20 companies per batch
  - Concurrent API calls for each company
  - Real-time progress tracking with time estimates

- Company Information Extraction:
  - Basic company details (establishment date, listing status)
  - Industry classification and track name
  - Parent company information
  - Stock reform status and timing
  - Funding history analysis
  - Founder information
  - Product and company descriptions

- Advanced Analysis:
  - Peer fund investment tracking
  - Multiple funding rounds detection
  - Multiple investors per round analysis
  - Deal list cross-referencing
  - Industry attribute classification

## Requirements

- Python 3.x
- pandas
- aiohttp
- requests
- openpyxl
- python-dotenv
- jinja2

## Setup

1. Clone the repository:
```bash
git clone https://github.com/dlwaterloo/lcp-manufacturing-companies-data-etl-pipeline.git
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
│   │   └── xiniu_api_client.py
│   └── utils/           # Utility functions
│       ├── check_pf_list.py
│       └── process_xiaojuren.py
├── data/
│   ├── input/         # Input Excel files
│   └── output/        # Generated output files
├── run_xiaojuren_formatted.py  # Main processing script
├── requirements.txt
└── README.md
```

## Usage

1. Place your input Excel file in the `data/input` directory
2. Run the main script:
```bash
python run_xiaojuren_formatted.py
```

The script will:
- Process up to 500 companies per sheet
- Run in batches of 20 companies in parallel
- Show real-time progress and time estimates
- Save results to `data/output` directory

## Input Format

The input Excel file should have sheets with a company name column (either '示范企业名称' or '企业名称').

## Output

The script generates an enriched Excel file with additional columns:
- 成立时间 (Establishment Date)
- 是否上市 (Listed Status)
- 母公司 (Parent Company)
- 母公司是否上市 (Parent Company Listed Status)
- 融资历史 (Funding History)
- Peer Fund (Peer Fund Investments)
- 某一年融资超2次 (Multiple Fundings in One Year)
- 单轮3家以上fund (Multiple Investors per Round)
- 2家以上Peer Fund (Multiple Peer Funds)
- 已在Deal List (In Deal List)
- 行业属性 (Industry Attributes)
- 赛道名称 (Track Name)
- 产品/公司介绍 (Product/Company Description)
- 创始人信息 (Founder Information)
- 是否是股份公司 (Stock Reform Status)
- 股改时间 (Stock Reform Time)

## Performance

- Each company's data is gathered through parallel API calls
- Companies are processed in batches of 20 for optimal throughput
- Progress tracking shows:
  - Companies processed
  - Average time per company
  - Estimated time remaining
  - Total processing time

## Security Notes

- API credentials are stored in `.env` file (not in version control)
- Input/output Excel files are excluded from git tracking
- All API calls use secure authentication

## License

MIT License
