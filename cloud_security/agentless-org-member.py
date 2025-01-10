import os
import json
import requests
import argparse
import logging
import pandas as pd
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

# Add changes here
def agentless_member_update(base_url, token, org_id, members):
    url = f"https://{base_url}/cas/api/v1/org/{org_id}/features"
    headers = {"content-type": "application/json","Accept": "application/json", "x-redlock-auth": token}
    query = {"memberIds":members,"features": [{"name": "Agentless Scanning","state": "disabled"}]}
    payload = json.dumps(query)

    response = requests.put(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        print(response.json()["message"])
        print(members)
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

    org_id = 627194092332
    member_ids = ["sorton-nonmanaged","sorton-ai-project"]

    agentless_update = agentless_member_update(url, token, org_id, member_ids)
       

    if token is None:
        logger.error("Unable to authenticate.")
        return

    

    logger.info(f"======================= END =======================")

if __name__ == "__main__":
    main()
   

