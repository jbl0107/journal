import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import Mock

from schemas.user import UserRead
from models.user import User

from main import app
from db import get_db


client = TestClient(app)



@pytest.fixture
def mock_db_session():
    ''' 
    Fixture que crea una sesión mock para endpoints que dependen de `get_db`.
    - Sobrescribe `get_db` para usar la sesión mock en lugar de la DB real.
    - Solo afecta a este test en memoria y se limpia automáticamente después.
    '''
    mock_session = Mock()


    def override_get_db():
        yield mock_session

    # Sobrescribimos la dependencia `get_db` para que el endpoint use nuestra sesión mock durante el test, evitando tocar la BD.
    # Esto solo afecta a este test en memoria y se limpia al final con `.pop()` para que no interfiera a otros tests
    app.dependency_overrides[get_db] = override_get_db

    yield mock_session

    app.dependency_overrides.pop(get_db, None)



@pytest.fixture(params=[
    [],
    [User(id=1, first_name='Pepe', last_name = 'ultmo', username = 'pep_ul', age  = 24)],
    [
        User(id=1, first_name='Pepe', last_name = 'ultmo', username = 'pep_ul', age  = 24),
        User(id=2, first_name='mauel', last_name = 'tto', username = 'm_t', age  = 20),
        User(id=3, first_name='rup', last_name = 'qq', username = 'repq', age  = 25)
    ]
], ids=['empty', 'single_user', 'multiple_users'])
def user_list(mock_db_session, request):
    mock_db_session.scalars.return_value.all.return_value = request.param
    return request.param


def test_get_all_users_exists(user_list):
    '''
    Test básico para asegurar que el endpoint `/users` responde 200 OK.
    No valida contenido, solo disponibilidad.
    '''
    
    response = client.get('/users')
    assert response.status_code == status.HTTP_200_OK



def test_get_all_users_data(user_list):
    """
    Test unitario del endpoint `/users` usando una sesión mock.
    - Valida que la respuesta contenga exactamente los datos esperados.
    """
    response = client.get('/users')
    assert response.json() == [UserRead.model_validate(fu).model_dump() for fu in user_list]




def test_get_by_id_ok(mock_db_session):
    '''
    Test unitario básico para validar que el endpoint get_by_id responde 200 OK
    cuando el usuario con el id especificado existe
    '''
    mock_db_session.scalar.return_value = User(id=1, first_name='Pepe', last_name = 'ultmo', username = 'pep_ul', age  = 24)
    response = client.get(f'/users/{1}')
    assert response.status_code == status.HTTP_200_OK


def test_get_by_id_not_found(mock_db_session):
    '''
    Test unitario básico para validar que el endpoint get_by_id responde 404 NOT FOUND
    cuando no existe el usuario con el id especificado
    '''
    mock_db_session.scalar.return_value = None
    response = client.get(f'/users/{11}')
    assert response.status_code == status.HTTP_404_NOT_FOUND


