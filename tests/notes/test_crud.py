from crud.note import get_notes, get_note_by_id, create_note, update_note, delete_note
from models.note import Note
from models.user import User
from schemas.note import NoteCreate, NoteUpdate, NotePatch
from exceptions.note_exceptions import UserNotFound


import pytest


## FIXTURE ##

@pytest.fixture
def note(user_pepe):
    return Note(id=1, title='Titulo 1', description='Descripción 1', user_id=1, user=user_pepe)


@pytest.fixture(params=[
    NoteUpdate(title='Nuevo titulo', description='Nueva description'),
    NotePatch(title='Cambio en el titulo')
], ids=['put', 'patch'])
def note_put_patch(request):
    return request.param


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


def test_create_note_user_not_found(magic_mock_session, note, subtests):
    '''
    Test unitario que comprueba que el CRUD create_note lanza la
    excepcion UserNotFound cuando el usuario con id especificado no existe
    '''

    magic_mock_session.get.return_value = None

    with subtests.test('raises UserNotFound when user not found'):
        with pytest.raises(UserNotFound):
            create_note(magic_mock_session, NoteCreate.model_validate(note))


    with subtests.test('begin called once'):
        magic_mock_session.begin.assert_called_once()

    with subtests.test('get called once with'):
        magic_mock_session.get.assert_called_once_with(User, note.user_id)

    with subtests.test('add not called'):
        magic_mock_session.add.assert_not_called()


def test_update_note_ok(magic_mock_session, note, note_put_patch, subtests):
    '''Test que valida actualización exitosa (PUT/PATCH) de nota existente'''

    magic_mock_session.get.return_value = note

    result = update_note(magic_mock_session, note.id, note_put_patch)

    with subtests.test('data validation'):
        if isinstance(note_put_patch, NoteUpdate):
            NoteUpdate.model_validate(result) == note_put_patch
        else:
            assert all(getattr(result, field) == getattr(note_put_patch, field) for field in note_put_patch.model_fields_set)

    with subtests.test('begin called once'):
        magic_mock_session.begin.assert_called_once()

    with subtests.test('get called once with'):
        magic_mock_session.get.assert_called_once_with(Note, note.id)


def test_update_note_not_found(magic_mock_session, note_put_patch, subtests):
    '''Test que valida que update_note devuelve None cuando la nota no existe'''

    magic_mock_session.get.return_value = None
    note_id = 1000
    result = update_note(magic_mock_session, note_id, note_put_patch)

    with subtests.test('result is None'):
        assert result is None

    with subtests.test('begin called once'):
        magic_mock_session.begin.assert_called_once()

    with subtests.test('get called once with'):
        magic_mock_session.get.assert_called_once_with(Note, note_id)


def test_delete_ok(magic_mock_session, note, subtests):
    '''
    Test unitario que prueba el borrado de
    un usuario registrado en el sistema
    '''

    magic_mock_session.get.return_value = note

    note_id = 1
    result = delete_note(magic_mock_session, note_id)


    with subtests.test('get called once with'):
        magic_mock_session.get.assert_called_once_with(Note, note_id)

    with subtests.test('begin and delete called once'):
        magic_mock_session.begin.assert_called_once()
        magic_mock_session.delete.assert_called_once_with(note)

    with subtests.test('data returned'):
        assert result is note


def test_delete_note_none(magic_mock_session, subtests):
    '''
    Test unitario que prueba el intento de borrado
    de una note no registrada en el sistema
    '''
    
    magic_mock_session.get.return_value = None

    note_id = 111
    result = delete_note(magic_mock_session, note_id)

    with subtests.test('get called once with'):
        magic_mock_session.get.assert_called_once_with(Note, note_id)

    with subtests.test('begin called'):
        magic_mock_session.begin.assert_called_once()

    with subtests.test('delete not called'):
        magic_mock_session.delete.assert_not_called()

    with subtests.test('data returned'):
        assert result is None
