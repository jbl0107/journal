import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import Mock

from schemas.user import UserRead 

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

    # Sobrescribimos la dependencia `get_db` para que el endpoint use
    # nuestra sesión mock durante el test, evitando tocar la base de datos real.
    # Esto solo afecta a este test en memoria y se limpia al final con `.pop()` para
    # que no interfiera a otros tests
    app.dependency_overrides[get_db] = override_get_db

    yield mock_session

    app.dependency_overrides.pop(get_db, None)
      

def test_get_all_users_exists():
    '''
    Test básico para asegurar que el endpoint `/users` responde 200 OK.
    No valida contenido, solo disponibilidad.
    '''
    response = client.get('/users')
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.parametrize('fake_users', (
    [],
    [UserRead(id=1, first_name='Pepe', last_name = 'ultmo', username = 'pep_ul', age  = 24)],
    [
        UserRead(id=1, first_name='Pepe', last_name = 'ultmo', username = 'pep_ul', age  = 24),
        UserRead(id=2, first_name='mauel', last_name = 'tto', username = 'm_t', age  = 20),
        UserRead(id=3, first_name='rup', last_name = 'qq', username = 'repq', age  = 25)
    ]
), ids=['empty', 'single_user', 'multiple_users'])
def test_get_all_users_data(mock_db_session, fake_users):
    """
    Test unitario del endpoint `/users` usando una sesión mock.
    - Valida que la respuesta contenga exactamente los datos esperados.
    """

    mock_db_session.scalars.return_value.all.return_value = fake_users

    response = client.get('/users')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == [fu.model_dump() for fu in fake_users]
