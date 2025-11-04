from crud.note import get_notes, get_note_by_id, create_note
from models.note import Note
from schemas.note import NoteCreate

import pytest


## FIXTURE ##

@pytest.fixture
def note(user_pepe):
    return Note(id=1, title='Titulo 1', description='Descripción 1', user_id=1, user=user_pepe)

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


@pytest.mark.parametrize('note', [
    Note(id=1, title='Titulo 1', description='Descripción 1', user_id=1),
    None
], ids=['note', 'None'])
def test_get_note_by_id(mock_session, note, subtests):
    '''
    Test unitario que comprueba si la operación CRUD get_by_id
    devuelve los datos correctos. También comprueba la estructura SQL
    '''
    mock_session.get.return_value = note

    note_id = 1
    with subtests.test('data'):
        assert get_note_by_id(mock_session, note_id) == note

    with subtests.test('get called once'):
        mock_session.get.assert_called_once()

    with subtests.test('get parameters'):
        mock_session.get.assert_called_once_with(Note, note_id)
    


def test_create_note_ok(magic_mock_session, note, subtests):
    '''
    Test unitario que comprueba el funcionamiento de la función CRUD
    create_note en un caso exitoso (inserta una nueva Note correctamente)
    ''' 

    result = create_note(magic_mock_session, NoteCreate.model_validate(note))
    called_note = magic_mock_session.add.call_args.args[0]

    fields = ['title', 'description', 'user_id']

    with subtests.test('correct fields passed to add'):
         assert isinstance(called_note, Note)
         for field in fields:
             assert getattr(called_note, field) == getattr(note, field)

    with subtests.test('correct return value from create_note'):
        assert isinstance(result, Note)
        for field in fields:
            assert getattr(result, field) == getattr(note, field)
    
    with subtests.test('add called once'):
        magic_mock_session.add.assert_called_once()

    with subtests.test('begin called once'):
        magic_mock_session.begin.assert_called_once()