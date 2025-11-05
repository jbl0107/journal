from main import app
from db import get_db
from models.user import User

import pytest
from unittest.mock import Mock, MagicMock
from sqlalchemy.orm import Session


@pytest.fixture
def mock_session():
    '''Mock de SQLAlchemy Session'''
    return Mock()


@pytest.fixture
def mock_db_session():
    ''' 
    Fixture que crea una sesión Mock para endpoints que dependen de `get_db`.
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


@pytest.fixture
def magic_mock_session():
    '''Mock de SQLAlchemy Session con spec para verificar métodos.'''
    return MagicMock(spec=Session)
