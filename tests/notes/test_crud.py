from crud.note import get_notes
from models.note import Note
from models.user import User

import pytest
from unittest.mock import Mock


## FIXTURE ##

@pytest.fixture
def mock_session():
    '''Mock de SQLAlchemy Session'''
    return Mock()
    

## FIN FIXTURE ##

@pytest.mark.parametrize('notes', (
    [],
    [Note(id=1, title='Titulo 1', description='Descripción 1', user_id=1)],
    [
        Note(id=1, title='Titulo 1', description='Descripción 1', user_id=1), 
        Note(id=2, title='Titulo con 20 caract', description='Otra descripción más larga', user_id=1)
    ]
), ids=['empty list', 'one note', 'limit notes'])
def test_get_notes(mock_session, notes, subtests):
    ''' 
    Test unitario que determina si la función CRUD get_notes devuelve
    los datos correctos, además de comprobar la estructura del SQL
    '''

    mock_session.scalars.return_value.all.return_value = notes
    result = get_notes(mock_session)

    with subtests.test('data'):
        assert result == notes

    with subtests.test('methods call'):
        mock_session.scalars.assert_called_once()
        mock_session.scalars.return_value.all.assert_called_once()

    with subtests.test('table select'):
        called_select =  mock_session.scalars.call_args.args[0]
        called_select.columns_clause_froms[0].name == Note.__table__.name



