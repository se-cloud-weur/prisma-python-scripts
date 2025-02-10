import os
import csv
import json
import requests
import argparse
import logging
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


            
def onboard_subscription(base_url, token, subscription_id, prisma_name, tenant_id, app_id, appsecret, sp_id):
    url = f"https://{base_url}/cas/v1/azure_account"
    headers = {"content-type": "application/json","Accept": "application/json", "x-redlock-auth": token}
    payload = json.dumps({
        "cloudAccount": 
        {
            "accountId": subscription_id,
            "enabled": "true",
            "groupIds": [],
            "name": prisma_name
        },
        "clientId": app_id,
        "key": appsecret,
        "monitorFlowLogs": False,
        "tenantId": tenant_id,
        "servicePrincipalId": sp_id
        })

    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        logger.info(f"Onboarded Subscription ID: {subscription_id} with the Prisma Name: {prisma_name}")
        return response
    else:
        logger.error(f"API Response: {response.status_code}")
        
         
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

    #Load items from .env file or environment variables
    load_dotenv ()
    url = os.environ.get("PRISMA_API_URL")
    identity = os.environ.get("PRISMA_ACCESS_KEY")
    secret = os.environ.get("PRISMA_SECRET_KEY")

    if not url or not identity or not secret:
        logger.error("PRISMA_API_URL, PRISMA_ACCESS_KEY, PRISMA_SECRET_KEY variables are not set.")
        return

    #Login to Prisma Cloud and Compute and get token
    token = login_saas(url, identity, secret)
    if token is None:
        logger.error("Unable to authenticate.")
        return

    #Get Azure details from prompt
    logger.info(f"======================= Get Azure Details =======================")
    print("What is the Application Client ID (app registration)")
    app_id = input()

    print("What is the Azure Tenant ID")
    tenant_id = input()

    print("What is the Application Secret")
    appsecret = input()

    print("What is the Service Principal ID (Enterprise App Object ID)")
    sp_id = input()

    #Loop through csv file and send API call

    logger.info(f"======================= Loop through CSV file =======================")
    with open('azure_details.csv') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            subscription_id = row["subscription_id"]
            prisma_name = row["prisma_name"]
            pc_query = onboard_subscription(url, token, subscription_id, prisma_name, tenant_id, app_id, appsecret, sp_id)

    
  
    logger.info(f"======================= END =======================")

if __name__ == "__main__":
    main()
   

