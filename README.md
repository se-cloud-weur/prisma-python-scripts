# Prisma Python tools

There are various scripts to help with data extraction from Prisma Cloud

## Setup Instructions

### Prerequisites

- Python 3.x
- Prisma Cloud API credentials




## Installation

1. **Create Python Virtual Environment (If you haven't alread)y**:

```bash
python3 -m virtualenv venv && source venv/bin/activate  
```

2. **Install required packages, each folder may have different requirements:**

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

## Prisma Cloud API Credentials
```
PRISMA_API_URL=<your_prisma_cloud_api_url>
PRISMA_ACCESS_KEY=<your_prisma_access_key>
PRISMA_SECRET_KEY=<your_prisma_secret_key>
```

## Usage

To use any scripts, simply run it in a terminal or pipeline:

```
python vuln-query-download.py

```


## Scripts available:

Scripts are available in the following high level folders dependent on their relevant function
- application security
- cloud security
- runtime security


### Cloud Security
```
vuln-query-download.py
```
Vulnerability export from the unified dashboard, An RQL can be provided for customisation and the results will get delivered to a csv file. This can be used for code, deploy and runtime assets and can include filters such as risk factors. Edit the query variable to change what details need to be seen. Examples are available here:

 [Vulnerability Query Examples](https://docs.prismacloud.io/en/enterprise-edition/content-collections/search-and-investigate/vulnerability-queries/vulnerability-query-examples)



### Runtime Security
```
defender-details.py
```
Gets defender details from the runtime security console. This is useful for getting specific version information including kernel information from the deployed defenders. In the console this is located under Runtime Security\Manage\Defenders clicking on a defender and looking at the summary. The script exports all details and kernel only details to a csv

