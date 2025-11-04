from schemas.note import NoteRead
from models.note import Note
from models.user import User
from main import app
from tests.shared_helpers import call_endpoint
from .constants import BASE_URL

import pytest
from fastapi.testclient import TestClient
from fastapi import status

client = TestClient(app)


## FIXTURE ##


## FIN FIXTURE ##


@pytest.mark.parametrize('notes', [
    [],
    [Note(id=1, title='Titulo', description='descripcion', user_id=1)], 
    [
        Note(id=1, title='Titulo', description='descripcion', user_id=1),
        Note(id=2, title='Titulo 2', description='descripcion 2', user_id=1),
        Note(id=3, title='Titulo 3', description='descripcion 3', user_id=1)
    ]
], ids=['empty list', 'one-note list', 'some-note list'])
def test_get_all(mock_db_session, notes, subtests):
    '''
    Test que valida que el endpoint /users devuelve 200 OK junto
    con los datos correctos
    '''
    user = User(id=1, first_name='Pepe', last_name = 'Rodriguez', username = 'pep_ul', age = 24)
    for n in notes:
        n.user = user
    
    mock_db_session.scalars.return_value.all.return_value = notes
    result = call_endpoint(client=client, method='get', base_url=BASE_URL)

    with subtests.test('status code'):
        assert result.status_code == status.HTTP_200_OK

    
    with subtests.test('data'):
        assert result.json() == [NoteRead.model_validate(n).model_dump() for n in notes]


