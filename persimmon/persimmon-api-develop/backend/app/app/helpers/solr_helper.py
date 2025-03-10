import json
import requests
import httpx
import os
import uuid
from typing import Dict
from fastapi import HTTPException

SOLR_BASE_URL=os.getenv("SOLR_BASE_URL")
SOLR_URL = f'{SOLR_BASE_URL}/resumes/update/json/docs?overwrite=true'
SOLR_URL_Query = f'{SOLR_BASE_URL}/resumes/select'


async def upload_to_solr( flattened_resume: dict) -> dict:
    """
    Upload a flattened resume to Solr.
    
    :param solr_url: Solr endpoint URL.
    :param flattened_resume: The resume JSON (flattened format).
    :return: A response message indicating success or failure.
    """
    # Convert the flattened_resume to JSON format
    json_data = json.dumps(flattened_resume)
    solr_url = SOLR_URL
    try:
        # Send the JSON data to Solr
        response = requests.post(
            solr_url,
            headers={"Content-Type": "application/json"},
            data=json_data,
            verify=False
        )
        
        # Check if the request was successful
        if response.status_code == 200:
            return {"message": "Document uploaded successfully" ,"status_code": response.status_code}
        else:
            return {"message": f"Error uploading document: {response.text}", "status_code": response.status_code}
    
    except requests.exceptions.RequestException as e:
        # Handle any exceptions during the request
        return {"message": f"Failed to connect to Solr: {str(e)}", "status_code": response.status_code}


async def query_solr(job_code , stage_uuid):
    if job_code:
        query = f"job_code:\"{job_code}\""
    if stage_uuid:
        query = f"stage_uuid:\"{stage_uuid}\""
    headers = {"Content-Type": "application/json"}
    query_params = {
        "q": query
         # Added to ensure a unique query each time
    }

    async with httpx.AsyncClient(verify=False) as client:
        response = await client.get(SOLR_URL_Query, params=query_params, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()


async def query_solr_with_filters(query: str, filters: Dict[str, str], rows: int = 20,start :int=0,exclude:str=None):
    headers = {"Content-Type": "application/json"}
    solr_payload = {
        "params": {
            "q": query,
            "defType": "edismax",
            "indent": "true",
            "fl": "*,score",
            "q.op": "OR",
            "rows": str(rows),
            "fq":exclude,
            "start":start,
            "bq": filters  # Include filters here as fq (filter query)
        }
        # Applying filters separately as filter queries
    }

    async with httpx.AsyncClient(verify=False) as client:
        response = await client.post(SOLR_URL_Query, json=solr_payload, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()


async def update_solr_documents_partially(uuids: list[str],set_uuid:uuid,search_category: str):
    headers = {"Content-Type": "application/json"}
    params = {
        "q": f"{search_category}:({' OR '.join(uuids)})", 
        "rows": len(uuids),
        "wt": "json"
    }

    async with httpx.AsyncClient(verify=False) as client:
        solr_response = await client.get(f"{SOLR_URL_Query}", params=params, headers=headers)
        documents = solr_response.json().get("response", {}).get("docs", [])
        updates = []
        for document in documents:
            uuid = document["applicant_uuid"] if search_category == "applicant_uuid" else document["stage_uuid"]
            if uuid in uuids:
                updates.append({
                    "id": document["id"],  
                    "stage_uuid": {"set": set_uuid}  
                })

        if not updates:
            raise HTTPException(status_code=404,detail="No matching documents found to update in solr")
        update_url = f"{SOLR_BASE_URL}/resumes/update?commit=true"
        try:
            print('calling post')
            update_response = await client.post(update_url, json=updates)
            print('updated_response',update_response)
        except httpx.RequestError as e:
            print(f"Request error occurred: {e}")
            raise HTTPException(status_code=update_response.status_code,detail=update_response.text)
        # TODO: Investigate 500 error coming from solr after atomic update happened successfully

async def is_applicant_exist(applicant_uuid: str):
    url = f"{SOLR_BASE_URL}/resumes/select"
    params = {
        "q": f"applicant_uuid:\"{applicant_uuid}\"",                
        "rows": 10,             
        "fl": "id,applicant_uuid", 
    }
    response = requests.get(url, params=params, verify=False)
    data = response.json()
    res = data['response']['numFound']
    return res