import os
import json
import requests
import argparse
import logging
import pandas as pd
from dotenv import load_dotenv

logger = logging.getLogger()

#Login to the SaaS Platform with Access Key and Secrets and returns the token
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

#Get the Compute URL in case it is needed for Compute queries
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

#Logon to Compute for Runtime Security queries
def login_compute(base_url, access_key, secret_key):
    url = f"{base_url}/api/v1/authenticate"
    payload = json.dumps({"username": access_key, "password": secret_key})
    headers = {"content-type": "application/json; charset=UTF-8"}
    try: 
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
    except requests.exceptions.RequestException as err:
        logger.error("Oops! An exception occurred logging onto compute, ", err)
        return None
    
    return response.json()["token"]

#Gets detailed information from defenders deployed in the environment
def defenderinfo(base_url, token):
    logger.info(f"Connect via the Prisma API")

    all_results = []
    offset = 0
    # filtered to Linux hosts
    url = f"{base_url}/api/v33.01/defenders?type=serverLinux" #Change path parameters for different queries
    headers = {"content-type": "application/json; charset=UTF-8", "Authorization": "Bearer " + token}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
        total_count = int(response.headers["Total-count"])
        print(f"Total Number of Defenders",total_count)
        
        
            
        # Split the query into offset of 50 (API limit) based on the total count of resources, extend them to a dataset
        for offset in range(0, total_count, 50):
            nexturl = f"{base_url}/api/v33.01/defenders?type=serverLinux&offset={offset}"
            next_response = requests.get(nexturl, headers=headers).json()
            all_results.extend(next_response)
       
    except requests.exceptions.RequestException as err:
        logger.error("Oops! An exception occurred getting defender details, ", err)
        return None

    logger.info(f"Return results to the dataset")
    return all_results
       

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

    #Get details from .env file
    load_dotenv ()
    url = os.environ.get("PRISMA_API_URL")
    identity = os.environ.get("PRISMA_ACCESS_KEY")
    secret = os.environ.get("PRISMA_SECRET_KEY")
    
    if not url or not identity or not secret:
        logger.error("PRISMA_API_URL, PRISMA_ACCESS_KEY, PRISMA_SECRET_KEY variables are not set.")
        return

    #Run Main Application 
    token = login_saas(url, identity, secret)
    compute_url = get_compute_url(url, token)
    compute_token = login_compute(compute_url, identity, secret)
    defender_detail = defenderinfo(compute_url, compute_token)
    
    if defender_detail != []:
        # Output Full details to csv (filtered_output.csv)
        logger.info(f"Normalize the data and output full details to csv")
        full_output = pd.json_normalize(defender_detail)
        full_output.to_csv("filtered_output.csv", index=False)

        # Output Hostname and Kernel Version Only (filtered_hostname_kernel.csv)
        logger.info(f"extract hostname and kernel data to csv")
        kernelOnly = (full_output[["hostname", "systemInfo.kernelVersion"]])
        kernelOnly.to_csv("filtered_hostname_kernel.csv", index=False)
    else:
        return None


    if token is None:
        logger.error("Unable to authenticate.")
        return

    logger.info(f"======================= END =======================")

if __name__ == "__main__":
    main()
   

