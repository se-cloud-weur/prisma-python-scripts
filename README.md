# Prisma Python tools

There are various scripts to help with data extraction from Prisma Cloud

## Setup Instructions

### Prerequisites

- Python 3.x
- Prisma Cloud API credentials (Access key and Secret)




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

### Application Security
```
appsec-iac-issues.py
appsec-licenses-issues.py
appsec-secrets-issues.py
appsec-vuln-issues.py
```
Application security issues from the Project part of the Application Security module. The issues have been broken down into IaC, Licenses, Secrets and Vulnerabilities. All data is retrieved and written to a csv file.

It is worth noting that the Vulnerability query that may be preferred is the one specified in the Cloud Security section as it provides more details.





### Cloud Security
```
vuln-query-download.py
```
Vulnerability export from the unified dashboard, An RQL can be provided for customisation and the results will get delivered to a csv file. This can be used for code, deploy and runtime assets and can include filters such as risk factors. Edit the query variable to change what details need to be seen. Examples are available here:

 [Vulnerability Query Examples](https://docs.prismacloud.io/en/enterprise-edition/content-collections/search-and-investigate/vulnerability-queries/vulnerability-query-examples)

```
agentless-org-member.py
```
This script will update the member accounts of an AWS Org, Azure Tenant or GCP org by inputting the project/account names in the csv file members_accounts.csv. A sample csv file is attached. The script will prompt for the org id as you can only update one at a time.

```
add_rs_label_iam_policy.py
```
This script will update the policies based on the ID's in the csv file iam_policyIds_4thFeb.csv. A sample csv file is attached. The script will update each policy to add the label 'Retain_Severity' to make sure the severity remains unchnaged when a PC update is pushed.

```
azure-subscription-onboarding.py
azure-details.csv
```
This script will onboard Azure subscriptions defined in a csv file. The scripts loops through the csv file and uses a common app registration. It assumes the app registration, custom roles and role assignments have been completed on the Azure side.  

### Runtime Security
```
defender-details-filtered.py
defender-details-full.py
```
Gets defender details from the runtime security console. This is useful for getting specific version information including kernel information from the deployed defenders. In the console this is located under Runtime Security\Manage\Defenders clicking on a defender and looking at the summary. The scripts exports all details and kernel only details to a csv. One is filtered to a type of defender, the other exports all details

