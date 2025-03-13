import requests
from fastapi import HTTPException
from typing import Optional
from datetime import datetime, timezone, timedelta
from app.helpers import db_helper as dbh
from sqlalchemy.orm import Session

def get_access_token(client_id,client_secret,code:str=None,redirect_uri:str=None,refresh_token:str=None):
    try:
        token_url = "https://zoom.us/oauth/token"
        encoded_code = requests.auth._basic_auth_str(client_id,client_secret)
        print('encoded code',encoded_code)
        headers = {
            "Authorization": f"{encoded_code}",
            "Content-Type": "application/x-www-form-urlencoded"
        }
        data = {}
        if redirect_uri:
            data = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": redirect_uri
                }
        if refresh_token:
            data = {
                "grant_type": "refresh_token",
                "refresh_token": refresh_token
            }

        response = requests.post(token_url, headers=headers, data=data)
        response_json = response.json()
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response_json.get('reason'))

        return response_json
    except HTTPException as e:
        raise e

def create_meeting(data,user_id,token):
    try:
        url = f'https://api.zoom.us/v2/users/{user_id}/meetings'
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        print('data,user,token,',data,user_id,token)
        response = requests.post(url, headers=headers, data=data)
        print('zoomh response',response)
        response_json = response.json()
        print('zoomh response json',response_json)
        if response.status_code == 404:
            raise HTTPException(status_code=response.status_code, detail=response_json.get('message'))
        if response.status_code != 201:
            raise HTTPException(status_code=response.status_code, detail=response_json.get('reason'))

        return response_json
    except HTTPException as e:
        raise e

def get_users(token):
    try:
        url = f"https://api.zoom.us/v2/users"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(url, headers=headers)
        response_json = response.json()
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response_json.get('reason'))

        return response_json
    except HTTPException as e:
        raise e

def get_user_by_id(token,user_id):
    try:
        url = f"https://api.zoom.us/v2/users/{user_id}"
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(url, headers=headers)
        response_json = response.json()
        if response.status_code == 404 or response.status_code == 400:
            raise HTTPException(status_code=response.status_code, detail=response_json.get('message'))
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response_json.get('reason'))

        return response_json
    except HTTPException as e:
        raise e

def validate_access_token(credentials,integration,email,session: Session):
    if credentials.get('expires_in') < datetime.now(timezone.utc).isoformat():
        response = get_access_token(credentials['client_id'], credentials['client_secret'],refresh_token=credentials['refresh_token'])
        expires_in = datetime.utcnow() + timedelta(seconds=response.get('expires_in'))
        expires_in = expires_in.isoformat()
        credentials = {
            "client_id": credentials.get('client_id'),
            "client_secret": credentials.get('client_secret'),
            "redirect_uri": credentials.get('redirect_uri'),
            "refresh_token": response.get('refresh_token'),
            "access_token": response.get('access_token'),
            "expires_in": expires_in
        }
        integration.credentials.update(credentials)
        integration.meta.update(dbh.update_meta(meta=integration.meta, email=email))
        integration.update(session=session)
    else:
        response = credentials
    return response