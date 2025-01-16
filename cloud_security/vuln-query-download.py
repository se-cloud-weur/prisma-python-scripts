import os
import json
import requests
import argparse
import logging
import gzip
from dotenv import load_dotenv

logger = logging.getLogger()

def login_saas(base_url, access_key, secret_key):
    url = f"https://{base_url}/login"
    payload = json.dumps({"username": access_key, "password": secret_key})
    headers = {"content-type": "application/json; charset=UTF-8"}
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
    except Exception as e:
        logger.info(f"Error in login_saas: {e}")
        return None

    return response.json().get("token")

# Query the vulnerability database for various options. Query is a variable
def vuln_query(base_url, token, query_param):

    url = f"https://{base_url}/uve/api/v1/vulnerabilities/search/download"
    headers = {"content-type": "application/json","Accept": "application/octet-stream", "x-redlock-auth": token}

    #Change the query you wish to recieve data from, defined in investigate/vulnerabilities in prisma
    query = {"query": f"{query_param}"}
    payload = json.dumps(query)
    response = requests.post(url, headers=headers, data=payload, stream=True)

    if response.status_code == 200:
        logger.info("File Downloading")
        return response
    else:
        logger.error(f"API Response: {response.status_code}")
        logger.error(response.json())

    
       

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug logging.")    

    args = parser.parse_args()

    if args.debug:
        logging_level = logging.DEBUG
    else:
        logging_level = logging.INFO
    
    logging.basicConfig(level=logging_level,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        filename='app.log',
                        filemode='a')
    
    # Create a console handler
    console_handler = logging.StreamHandler()

    # Add the console handler to the logger
    logger.addHandler(console_handler)

    logger.info(f"======================= START =======================")
    if args.debug: 
        logger.info(f"======================= DEBUG MODE =======================")


    load_dotenv ()
    url = os.environ.get("PRISMA_API_URL")
    identity = os.environ.get("PRISMA_ACCESS_KEY")
    secret = os.environ.get("PRISMA_SECRET_KEY")
    
    if not url or not identity or not secret:
        logger.error("PRISMA_API_URL, PRISMA_ACCESS_KEY, PRISMA_SECRET_KEY variables are not set.")
        return

    #Login to Prisma Cloud and get token
    token = login_saas(url, identity, secret)

    #Get Query from Input
    print('Enter your vulnerability investigate query i.e.', "vulnerability where asset.type IN ('Host') AND severity IN ('high', 'critical')" )
    query_input = input()

    #Get host Vulnerabilities from runtime output and send to csv and json file. (Runs from Def section)
    vuln_query_output = vuln_query(url, token, query_input)

    with open('list-vuln.csv.gz', 'wb') as file:
       file.write(vuln_query_output.content)
       logger.info("Write Gzip to disk")


    # Convert to csv
    with gzip.open('list-vuln.csv.gz', 'rt', newline='') as csv_file:
        csv_data = csv_file.read()
        with open('list-vuln.csv', 'wt') as out_file:
            out_file.write(csv_data)
            logger.info("Extract CSV")


    if token is None:
        logger.error("Unable to authenticate.")
        return

    

    logger.info(f"======================= END =======================")

if __name__ == "__main__":
    main()
   

