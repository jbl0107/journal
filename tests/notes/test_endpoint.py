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

@pytest.fixture(params=[
    {'id': 1, 'title': 'Título', 'description': 'Descripción'},
    {'id': 2, 'title': 'Título 2', 'description': 'Descripción 2'}
], ids=['Note 1', 'Note 2'])
def note(request, user_pepe, mock_db_session):
    """Fixture parametrizado para notas con mock de la sesión."""
    data = request.param
    note_obj = Note(
        id=data['id'],
        title=data['title'],
        description=data['description'],
        user_id=user_pepe.id,
        user=user_pepe
    )

    mock_db_session.get.return_value = note_obj
    return note_obj

## FIN FIXTURE ##


## TESTS GET_ALL ##

@pytest.mark.parametrize('notes', [
    [],
    [Note(id=1, title='Titulo', description='descripcion', user_id=1)], 
    [
        Note(id=1, title='Titulo', description='descripcion', user_id=1),
        Note(id=2, title='Titulo 2', description='descripcion 2', user_id=1),
        Note(id=3, title='Titulo 3', description='descripcion 3', user_id=1)
    ]
], ids=['empty list', 'one-note list', 'some-note list'])
def test_get_all(mock_db_session, notes, user_pepe, subtests):
    '''
    Test que valida que el endpoint /notes devuelve 200 OK junto
    con los datos correctos
    '''
    for n in notes:
        n.user = user_pepe
    
    mock_db_session.scalars.return_value.all.return_value = notes
    result = call_endpoint(client=client, method='get', base_url=BASE_URL)

    with subtests.test('status code'):
        assert result.status_code == status.HTTP_200_OK

    with subtests.test('data'):
        assert result.json() == [NoteRead.model_validate(n).model_dump() for n in notes]



## TESTS GET_BY_ID ##

def test_get_by_id_ok(note, subtests):
    '''
    Test unitario para validar que el endpoint get_by_id devuelve un
    código 200 OK y que los datos son correctos 
    '''
    result = call_endpoint(client=client, method='get_by_id', base_url=BASE_URL, resource_id=note.id)

    with subtests.test('status code'):
        assert result.status_code == status.HTTP_200_OK

    with subtests.test('data'):
        assert result.json() == NoteRead.model_validate(note).model_dump()



def test_get_by_id_not_found(mock_db_session):
    '''
    Test unitario para validar que el endpoint get_by_id devuelve un
    404 NOT FOUND cuando la Note con id especificado no existe
    '''
    mock_db_session.get.return_value = None
    response = call_endpoint(client=client, method='get_by_id', base_url=BASE_URL, resource_id=110)

    assert response.status_code == status.HTTP_404_NOT_FOUND        

