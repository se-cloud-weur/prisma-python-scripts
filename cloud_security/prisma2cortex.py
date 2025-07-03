import os
import json
import requests
import argparse
import pandas as pd
from dotenv import load_dotenv


def login_saas(base_url, access_key, secret_key):
    url = f"https://{base_url}/login"
    payload = json.dumps({"username": access_key, "password": secret_key})
    headers = {"content-type": "application/json; charset=UTF-8"}
    try:
        response = requests.post(url, headers=headers, data=payload)
        response.raise_for_status()  # Raises a HTTPError if the status is 4xx, 5xx
    except Exception as e:
        print(f"Error in login_saas: {e}")
        return None

    return response.json().get("token")

# Query the asset inventory for asset classes
def asset_query(base_url, token):

    url = f"https://{base_url}/v3/inventory"
    headers = {"content-type": "application/json","Accept": "application/json", "x-redlock-auth": token}
    payload = json.dumps({
    "filters": [
        {
            "name": "asset.class",
            "operator": "=",
            "value": "Database"
        },
        {
            "name": "asset.class",
            "operator": "=",
            "value": "Compute"
        },
         {
            "name": "asset.class",
            "operator": "=",
            "value": "Storage"
        }

    ],
     "groupBy": [
         "resource.type"
     ] }
    )

    response = requests.post(url, headers=headers, data=payload)

    if response.status_code == 200:
        return response.json()["groupedAggregates"] #return only the aggregates not individual items
    else:
        print(f"API Response: {response.status_code}")
        print(response.json())




def main():

    load_dotenv ()
    url = os.environ.get("PRISMA_API_URL")
    identity = os.environ.get("PRISMA_ACCESS_KEY")
    secret = os.environ.get("PRISMA_SECRET_KEY")
    
    if not url or not identity or not secret:
        print("PRISMA_API_URL, PRISMA_ACCESS_KEY, PRISMA_SECRET_KEY variables are not set.")
        return

    #Login to Prisma Cloud and get token
    token = login_saas(url, identity, secret)

    if token is None:
        print("Unable to authenticate.")
        return

    #Run query against inventory api
    all_assets = asset_query(url, token)
    
    filtered_assets= pd.json_normalize(all_assets)[['cloudTypeName', 'resourceTypeName', 'totalResources']] #Filter assets to a few columns
    filtered_assets.rename(columns={'cloudTypeName': 'Cloud', 'resourceTypeName':'Asset Type', 'totalResources': 'Count'}, inplace=True)

    #Break down into different queries
    virtual_machines  = filtered_assets[filtered_assets['Asset Type'].isin(['Google Compute Engine VM Instance', 'Azure Virtual Machine', 'Azure Virtual Machine Scale Set VM', 'EC2 Instance', 'Virtual Machine' ])]
    serverless = filtered_assets[filtered_assets['Asset Type'].isin(['Lambda Function', 'Google Cloud Function', 'Azure Cloud Function'])]
    caas = filtered_assets[filtered_assets['Asset Type'].isin(['ECS Fargate Container', 'ECS Container Instance', 'ECS Task Definition','ECS Service', 'ECS Fargate', 'Google Cloud Run Service', 'Azure Container Instances Container Group'  ])]
    databases  = filtered_assets[(filtered_assets['Asset Type'].isin(['RDS Database Instance', 'Amazon DynamoDB Table', 'Google BigQuery Dataset', 'Google Cloud SQL DB Instance', ' Google Cloud Bigtable' 'Azure SQL Server', 'Azure SQL Database', 'Azure SQL Managed Instance', 'Azure Cosmos DB']))]
    storage  = filtered_assets[filtered_assets['Asset Type'].isin(['S3 Bucket', 'Google Cloud Storage Bucket', 'Azure Storage Account Blob Container'  ])]
    
    space = '\n'

    print(2*space)
    print ('===============================Virtual machines===============================')
    print(space)
    print(virtual_machines.to_string(index=False))
    print(space)
    print ('===============================Serverless=====================================')
    print(space)
    print(serverless.to_string(index=False))
    print(space)
    print ('===============================CaaS===========================================')
    print(space)
    print(caas.to_string(index=False))
    print(space)
    print ('===============================Databases======================================')
    print(space)
    print(databases.to_string(index=False))
    print(space)
    print ('===============================Storage========================================')
    print(space)
    print(storage.to_string(index=False))
    print(space)

    #Write to CSV file
    virtual_machines.to_csv('prisma_assets.csv', index=False)
    serverless.to_csv('prisma_assets.csv', mode='a', index=False) #append to existing csv
    caas.to_csv('prisma_assets.csv', mode='a', index=False) #append to existing csv
    databases.to_csv('prisma_assets.csv', mode='a', index=False) #append to existing csv
    storage.to_csv('prisma_assets.csv', mode='a', index=False) #append to existing csv

if __name__ == "__main__":
    main()
   

