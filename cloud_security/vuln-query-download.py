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

def get_compute_url(base_url, token):
    url = f"https://{base_url}/meta_info"
    headers = {"content-type": "application/json; charset=UTF-8", "Authorization": "Bearer " + token}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
    except requests.exceptions.RequestException as err:
        logger.error("Oops! An exception occurred in get_compute_url, ", err)
        return None

    response_json = response.json()
    return response_json.get("twistlockUrl", None)

def login_compute(base_url, access_key, secret_key):
    url = f"{base_url}/api/v1/authenticate"
    payload = json.dumps({"username": access_key, "password": secret_key})
    headers = {"content-type": "application/json; charset=UTF-8"}
    response = requests.post(url, headers=headers, data=payload)
    return response.json()["token"]

# Add changes here
def vuln_query(base_url, token):

    url = f"https://{base_url}/uve/api/v1/vulnerabilities/search/download"
    headers = {"content-type": "application/json","Accept": "application/octet-stream", "x-redlock-auth": token}

    #Change the query you wish to recieve data from
    payload = json.dumps({"query": "vulnerability where asset.type IN ('Package', 'Host') AND severity IN ('high', 'critical')"})
    response = requests.post(url, headers=headers, data=payload, stream=True)
    if response.status_code == 200:
        return response
    else:
        print('API Call Failed')

    
       

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

    #Login to Prisma Cloud and Compute and get token
    token = login_saas(url, identity, secret)
    compute_url = get_compute_url(url, token)
    compute_token = login_compute(compute_url, identity, secret)

    #Get host Vulnerabilities from runtime output and send to csv and json file. (Runs from Def section)
    vuln_query_output = vuln_query(url, token)

    with open('list-vuln.csv.gz', 'wb') as file:
       file.write(vuln_query_output.content)


    # Convert to csv
    with gzip.open('list-vuln.csv.gz', 'rt', newline='') as csv_file:
        csv_data = csv_file.read()
        with open('list-vuln.csv', 'wt') as out_file:
            out_file.write(csv_data)


    if token is None:
        logger.error("Unable to authenticate.")
        return

    

    logger.info(f"======================= END =======================")

if __name__ == "__main__":
    main()
   

