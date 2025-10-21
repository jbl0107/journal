import pytest
from fastapi.testclient import TestClient
from fastapi import Response, status


def call_endpoint(client:TestClient, method:str, base_url:str, resource_id:int = None, payload:dict = None):
    '''Helper: llama a post o put segun method'''

    base_url = base_url.rstrip('/')

    if method == 'post':
        return client.post(f'{base_url}/', json=payload)
    
    elif method == 'put':
        assert resource_id is not None
        return client.put(f'{base_url}/{resource_id}', json=payload)

    raise ValueError('Método no soportado')


def assert_201_or_200(response:Response, method:str):
    if method == 'put':
        assert response.status_code == status.HTTP_200_OK

    elif method == 'post':
        assert response.status_code == status.HTTP_201_CREATED
