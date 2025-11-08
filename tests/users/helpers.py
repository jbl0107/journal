from fastapi import Response


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

