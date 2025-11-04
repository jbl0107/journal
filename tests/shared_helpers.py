from fastapi.testclient import TestClient

def call_endpoint(client:TestClient, method:str, base_url:str, resource_id:int | None = None, payload:dict | None = None):
    '''Helper: llama a get/get_by_id, post, put o delete segun method'''

    base_url = base_url.rstrip('/')

    if method == 'get':
        return client.get(f'{base_url}/')
    
    elif method == 'get_by_id':
        return client.get(f'{base_url}/{resource_id}')

    elif method == 'post':
        return client.post(f'{base_url}/', json=payload)
    
    elif method == 'put':
        assert resource_id is not None
        return client.put(f'{base_url}/{resource_id}', json=payload)
    
    elif method == 'patch':
        assert resource_id is not None
        return client.patch(f'{base_url}/{resource_id}', json=payload)
    
    elif method == 'delete':
        return client.delete(f'{base_url}/{resource_id}')

    raise ValueError('Método no soportado')