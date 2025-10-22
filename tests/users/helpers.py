import pytest
from fastapi.testclient import TestClient
from fastapi import Response, status


def call_endpoint(client:TestClient, method:str, base_url:str, resource_id:int | None = None, payload:dict | None = None):
    '''Helper: llama a post, put, delete segun method'''

    base_url = base_url.rstrip('/')

    if method == 'post':
        return client.post(f'{base_url}/', json=payload)
    
    elif method == 'put':
        assert resource_id is not None
        return client.put(f'{base_url}/{resource_id}', json=payload)
    
    elif method == 'delete':
        return client.delete(f'{base_url}/{resource_id}')

    raise ValueError('Método no soportado')


def assert_422(response:Response, subtests, *, context:str, field:str | None = None, msg:str | None = None, 
               label:str|None = None, key:str = 'type'):
    with subtests.test('status code'):
        assert response.status_code == 422

    if context == 'required_fields':
        required_fields(response, field, subtests)

    elif context == 'assert_field_error':
        assert_field_error(response, field, msg, subtests, label, key)
    
    

def required_fields(response:Response, required_field:str, subtests):
    with subtests.test(f'missing field {required_field} error'):
        assert response.json()['detail'][0]['loc'][1] == required_field


def assert_field_error(response:Response, field:str, msg:str, subtests, label:str|None, key:str):
    if label is None:
        label = f'{field} length'

    with subtests.test(label):
        json_detail = response.json()['detail'][0]
        assert json_detail[key] == msg and field in json_detail['loc']

