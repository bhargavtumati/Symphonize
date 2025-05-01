import json
import requests
import httpx
import os
import uuid
from typing import Dict, Optional
from fastapi import HTTPException

CONTENT_TYPE_JSON = "application/json"
SOLR_BASE_URL=os.getenv("SOLR_BASE_URL")
SOLR_URL = f'{SOLR_BASE_URL}/resumes/update/json/docs?overwrite=true'
SOLR_URL_Query = f'{SOLR_BASE_URL}/resumes/select'


async def upload_to_solr(flattened_resume: dict) -> dict:
    """
    Upload a flattened resume to Solr.
    
    :param solr_url: Solr endpoint URL.
    :param flattened_resume: The resume JSON (flattened format).
    :return: A response message indicating success or failure.
    """
    # Convert the flattened_resume to JSON format
    json_data = json.dumps(flattened_resume)
    response = None
    solr_url = SOLR_URL
    f"========= uploading function to solr for applicant_uuid: {flattened_resume['applicant_uuid']}"
    try:
        # Send the JSON data to Solr
        api_env = os.getenv("API_ENVIRONMENT", "").lower()
        verify_ssl = False if api_env == "qa" else True
        async with httpx.AsyncClient(
            timeout=httpx.Timeout(60, connect=60),
            verify=verify_ssl
            ) as client:
            response = await client.post(solr_url,
                headers={"Content-Type": "application/json"},
                data=json_data
            )
        
        # Check if the request was successful
        if response.status_code == 200:
            return {"message": "Document uploaded successfully" ,"status_code": response.status_code}
        else:
            return {"message": f"Error uploading document: {response.text}", "status_code": response.status_code}
    
    except httpx.HTTPStatusError as e:
        return {"message": f"HTTP error occurred: {str(e)}", "status_code": e.response.status_code}
    except httpx.ConnectTimeout:
        return {"message": "Failed to connect to Solr: Connection timed out", "status_code": 408}
    except httpx.RequestError as e:
        return {"message": f"Request error occurred: {str(e)}", "status_code": 500}
    except Exception as e:
        return {"message": f"Unexpected error: {str(e)}", "status_code": 500}

async def query_solr(job_code , stage_uuid:Optional[uuid.UUID] = None, rows: int = 10):
    if job_code:
        query = f"job_code:\"{job_code}\""
    if stage_uuid:
        query = f"stage_uuid:\"{stage_uuid}\""
    headers = {"Content-Type": CONTENT_TYPE_JSON}
    query_params = {
        "q": query,
        "rows" : rows
         # Added to ensure a unique query each time
    }

    api_env = os.getenv("API_ENVIRONMENT", "").lower()
    verify_ssl = False if api_env == "qa" else True
    async with httpx.AsyncClient(verify=verify_ssl) as client:
        response = await client.get(SOLR_URL_Query, params=query_params, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()


async def query_solr_with_filters(query: str, exclude:str=None):
    headers = {"Content-Type": CONTENT_TYPE_JSON}
    solr_payload = {
        "params": {
            "q": query,
            "defType": "edismax",
            "indent": "true",
            "fl": "*,score",
            "q.op": "OR",
            "fq":exclude,
            "rows": 10000,
            "start": 0
        }
    }

    api_env = os.getenv("API_ENVIRONMENT", "").lower()
    verify_ssl = False if api_env == "qa" else True
    async with httpx.AsyncClient(verify=verify_ssl) as client:
        response = await client.post(SOLR_URL_Query, json=solr_payload, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    return response.json()


async def update_solr_documents_partially(uuids: list[str],set_uuid:uuid,search_category: str):
    headers = {"Content-Type": CONTENT_TYPE_JSON}
    params = {
        "q": f"{search_category}:({' OR '.join(uuids)})", 
        "rows": len(uuids),
        "wt": "json"
    }

    api_env = os.getenv("API_ENVIRONMENT", "").lower()
    verify_ssl = False if api_env == "qa" else True
    async with httpx.AsyncClient(verify=verify_ssl) as client:
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

        if len(updates) > 0:
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
    headers = {"Content-Type": CONTENT_TYPE_JSON}
    params = {
        "q": f"applicant_uuid:\"{applicant_uuid}\"",                
        "rows": 20,             
        "fl": "id,applicant_uuid", 
    }

    api_env = os.getenv("API_ENVIRONMENT", "").lower()
    verify_ssl = False if api_env == "qa" else True
    async with httpx.AsyncClient(verify=verify_ssl) as client:
        response = await client.get(SOLR_URL_Query, params=params, headers=headers)

    if response.status_code != 200:
        raise HTTPException(status_code=response.status_code, detail=response.text)

    data = response.json()
    res = data['response']['numFound']
    return res


async def delete_records_by_applicant_uuid(applicant_uuid: str):
    """Delete records from Solr based on applicant_uuid."""
    if not applicant_uuid:
        return

    delete_query = {"delete": {"query": f'applicant_uuid:"{applicant_uuid}"'}}
    api_env = os.getenv("API_ENVIRONMENT", "").lower()
    verify_ssl = False if api_env == "qa" else True
    async with httpx.AsyncClient(verify=verify_ssl) as client:
        url = f"{SOLR_BASE_URL}/resumes/update?commit=true"
        response = await client.post(url, json=delete_query)
        return response.json()


async def get_solr_applicant_by_applicant_uuid(applicant_uuid,details:bool=False):
    api_env = os.getenv("API_ENVIRONMENT", "").lower()
    verify_ssl = False if api_env == "qa" else True
    async with httpx.AsyncClient(verify=verify_ssl) as client:
        try:
            if details: 
                response = await client.get(f"{SOLR_BASE_URL}/resumes/select", params={
                    "q": f"applicant_uuid:\"{applicant_uuid}\"",
                    "rows": 50
                }) 
            else:
                response = await client.get(f"{SOLR_BASE_URL}/resumes/select", params={
                    "q": f"applicant_uuid:\"{applicant_uuid}\"",
                    "rows": 50,
                    "fl": "id,applicant_uuid",
                })

            if response.status_code != 200:
                print(f"Solr request failed: {response.status_code} {response.text}")
                return []  # Return empty list to prevent crashes
            return response.json().get("response", {}).get("docs", [])
        except Exception as e:
            print(f"Error fetching data from Solr: {e}")
            return []


async def delete_solr_records(doc_ids):
    """Delete multiple records from Solr by ID."""
    if not doc_ids:
        return
    api_env = os.getenv("API_ENVIRONMENT", "").lower()
    verify_ssl = False if api_env == "qa" else True
    async with httpx.AsyncClient(verify=verify_ssl) as client:
        delete_query = {"delete": [{"id": doc_id} for doc_id in doc_ids]}
        url = f"{SOLR_BASE_URL}/resumes/update?commit=true"
        response = await client.post(url, json=delete_query)
        return response.json()


async def delete_duplicate_records(applicant_uuid):
    """Fetch records, find duplicates, and delete all except the first occurrence."""
    records = await get_solr_applicant_by_applicant_uuid(applicant_uuid)
    print(records)

    if not records:
        print(f"No records found with applicant_uuid : {applicant_uuid}")
        return
    duplicates_to_delete = []
    if len(records)>1:
        for record in records:
            duplicates_to_delete.append(record.get("id"))
        duplicates_to_delete.pop(0)
            
    if duplicates_to_delete:
        print(f"Deleting {(duplicates_to_delete)} duplicate records...")
        await delete_solr_records(duplicates_to_delete)
        print("Duplicates removed successfully.")
    else:
        print("No duplicates found.")


async def update_applicant_document(doc_id: str, update_fields: dict):
    
    url = f"{SOLR_BASE_URL}/resumes/update?commit=true"

    update_fields = [ {
        "id": doc_id,
        **update_fields
    } ]

    print(f"the updated fields {update_fields}")    
    api_env = os.getenv("API_ENVIRONMENT", "").lower()
    verify_ssl = False if api_env == "qa" else True
    async with httpx.AsyncClient(verify=verify_ssl) as client:
        update_response = await client.post(url, json=update_fields)
        update_response.raise_for_status()
    return update_response.json()
    