# Prisma Python tools

There are various scripts to help with data extraction from Prisma Cloud

## Setup Instructions

### Prerequisites

- Python 3.x
- Prisma Cloud API credentials

### Installation

1. **Create Python Virtual Environment (If you haven't alread)y**:

```bash
python3 -m virtualenv venv && source venv/bin/activate  
```

2. **Install required packages**:

Install the dependencies listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

3. **Environment Variables**:

Create a `.env` file in the root directory of your project. You can copy the `.env.example` file and update it with your own credentials:

```bash
cp .env.example .env
```

Update the `.env` file with your Prisma Cloud API credentials

```
# Prisma Cloud API Credentials
PRISMA_API_URL=<your_prisma_cloud_api_url>
PRISMA_ACCESS_KEY=<your_prisma_access_key>
PRISMA_SECRET_KEY=<your_prisma_secret_key>
```

### Options

Select from any of the following scripts:


vuln-rql-export.py

Vulnerability export from the unified dashboard, An RQL can be provided for customisation and the results will get delivered to a csv file.



### Usage
```
To use the script, simply run it in a terminal or pipeline:
bash
python vuln-query-download.py

```

### Output

The script will query the API, and deliver information via csv

