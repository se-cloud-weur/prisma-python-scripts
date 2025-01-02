import os
import json
import requests
import argparse
import logging
import gzip
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
def appsec_query(base_url, token):

    url = f"https://{base_url}/code/api/v2/code-issues/branch_scan"
    headers = {"content-type": "application/json", "authorization": token}
    all_results = []
    query = {
            "filters": {
                "checkStatus": "Error",
                "codeCategories": [
                "Licenses"
                ]
            },
            "useSearchAfterPagination": True,
            "limit": 1000
            }
    payload = json.dumps(query)
    response = requests.post(url, headers=headers, data=payload)
    all_results = response.json()["data"]

    #Prepare for Loop
    next_page = response.json()["hasNext"]
    count = 0
    while next_page == True:
        searchstring = response.json()["searchAfter"] #Look for Next Page
        searchAfter = {"searchAfter": searchstring} #Create new string to update payload
        updated_payload = json.loads(payload) 
        updated_payload.update(searchAfter) #Update the payload
        updated_payload = json.dumps(updated_payload) #return back to json string
        response = requests.post(url, headers=headers, data=updated_payload) #Updated response
        all_results.extend(response.json()["data"])
        next_page = response.json()["hasNext"]
        count += 1
        print ("Adding Page", count, "to the query results")
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


    load_dotenv ()
    url = os.environ.get("PRISMA_API_URL")
    identity = os.environ.get("PRISMA_ACCESS_KEY")
    secret = os.environ.get("PRISMA_SECRET_KEY")
    
    if not url or not identity or not secret:
        logger.error("PRISMA_API_URL, PRISMA_ACCESS_KEY, PRISMA_SECRET_KEY variables are not set.")
        return

    #Login to Prisma Cloud and Compute and get token
    token = login_saas(url, identity, secret)
    appsec_results = appsec_query(url, token)
 
    if appsec_results != []:
        # Output Full details to csv (full_output.csv)
        logger.info(f"Normalize the data and output full details to csv")
        full_output = pd.json_normalize(appsec_results)
        full_output.to_csv("appsec_licenses.csv", index=False)

    else:
        return None    

    if token is None:
        logger.error("Unable to authenticate.")
        return

    

    logger.info(f"======================= END =======================")

if __name__ == "__main__":
    main()
   

