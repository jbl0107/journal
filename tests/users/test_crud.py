import pytest
from crud.user import get_users, get_user_by_id, create_user, delete_user
from unittest.mock import Mock, MagicMock
from schemas.user import UserCreate
from models.user import User
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from exceptions.user_exceptions import UserAlreadyExists
from models.note import Note  # Necesario en runtime para que SQLAlchemy resuelva User.notes
# Aunque la tabla 'notes' ya exista en la base de datos, SQLAlchemy necesita la clase Note
# en memoria al crear el mapper de User. Esto asegura que la relación notes funcione correctamente durante los tests.


## FIXTURES ##
@pytest.fixture
def user():
    return User(first_name='Pepe', last_name = 'Ruiz', username = 'rai17', age  = 24, password='12345678')


@pytest.fixture
def magic_mock_session():
    return MagicMock(spec=Session)

## FIN FIXTURE ##



@pytest.mark.parametrize('users', (
    [],
    [User(id=1, first_name='Pepe', last_name = 'ultimo', username = 'pep_ul', age  = 24, password='123456')],
    [
        User(id=1, first_name='Pepe', last_name = 'ultimo', username = 'pep_ul', age  = 24, password='123456'),
        User(id=2, first_name='Lorem', last_name = 'ipsum', username = 'Manuel', age  = 33, password='123456')
    ]
), ids=['empty', 'single_user_list', 'some_users_list'])
def test_get_users(users, subtests):
    '''
    Test unitario que determina si la función crud get_users devuelve 
    los datos correctos, además de comprobar la estructura del SQL
    '''

    mock_scalar_result = Mock()
    mock_scalar_result.all.return_value = users

    mock_session = Mock()
    mock_session.scalars.return_value = mock_scalar_result


    result = get_users(mock_session)

    with subtests.test('data'):
        assert result == users

    with subtests.test('methods call'):
        mock_session.scalars.assert_called_once()
        mock_scalar_result.all.assert_called_once()

    called_select = mock_session.scalars.call_args.args[0]

    with subtests.test('table select'):
        assert called_select.columns_clause_froms[0].name == User.__table__.name



@pytest.mark.parametrize('user', (
        User(id=1, first_name='Pepe', last_name = 'ultimo', username = 'pep_ul', age  = 24, password='123456'),
        None
), ids=['user', 'None'])
def test_get_user_by_id(user, subtests): # subtests -> plugin detectado auto. por pytest como fixture
    '''
    Test que determina si la función crud get_user_by_id devuelve 
    los datos correctos, además de comprobar la estructura del SQL
    '''

    mock_session = Mock()
    mock_session.get.return_value = user

    # Cada bloque `with subtests` crea un subtest independiente,
    # permitiendo identificar exactamente qué assert falla sin perder los demás

    user_id = 1
    with subtests.test('return correct user'):
        assert get_user_by_id(mock_session, user_id) == user

    #Comprobar que se llama a get
    with subtests.test('calls get once'):
        mock_session.get.assert_called_once()

    with subtests.test('get parameters'):
        mock_session.get.assert_called_once_with(User, user_id)



def test_create_user_ok(magic_mock_session, user, subtests):
    '''
    Test unitario que comprueba el funcionamiento de la función CRUD create_user
    en un caso exitoso (inserción correcta de un nuevo usuario).
    '''
    
    result = create_user(UserCreate.model_validate(user), magic_mock_session)

    called_user:User = magic_mock_session.add.call_args.args[0]

    fields = ['first_name', 'last_name', 'username', 'age', 'password']

    with subtests.test('correct fields passed to add'):
        assert isinstance(called_user, User)
        for field in fields:
            assert getattr(called_user, field) == getattr(user, field)

    with subtests.test('correct return value from create_user'):
        assert isinstance(result, User)
        for field in fields:
            assert getattr(result, field) == getattr(user, field)
    
    with subtests.test('add called once'):
        magic_mock_session.add.assert_called_once()

    with subtests.test('begin called once'):
        magic_mock_session.begin.assert_called_once()



def test_create_user_error(magic_mock_session, user):
    '''
    Test unitario que comprueba el comportamiento de la función CRUD create_user
    cuando se intenta insertar un usuario con un username que ya existe
    (violación de la restricción de unicidad).
    '''

    mock_e_orig = Mock()
    mock_e_orig.diag.constraint_name = 'users_username_key'
    magic_mock_session.add.side_effect = IntegrityError(None, None, mock_e_orig) # cada vez que alguien llame a add, lanza esta exc

    with pytest.raises(UserAlreadyExists):
        create_user(user, magic_mock_session)



def test_delete_user_ok(magic_mock_session, user, subtests):
    '''
    Test unitario que prueba el borrado de
    un usuario registrado en el sistema
    '''
    
    magic_mock_session.get.return_value = user

    user_id = 1
    result = delete_user(magic_mock_session, user_id)
    
    with subtests.test('get called once with'):
        magic_mock_session.get.assert_called_once_with(User, user_id)

    with subtests.test('begin and delete called once'):
        magic_mock_session.begin.assert_called_once()
        magic_mock_session.delete.assert_called_once_with(user)

    with subtests.test('data returned'):
        assert result is user 


def test_delete_user_none(magic_mock_session, subtests):
    '''
    Test unitario que prueba el intento de borrado
    de un usuario no registrado en el sistema
    '''
    
    magic_mock_session.get.return_value = None

    user_id = 111
    result = delete_user(magic_mock_session, user_id)

    with subtests.test('get called once with'):
        magic_mock_session.get.assert_called_once_with(User, user_id)

    with subtests.test('begin called'):
        magic_mock_session.begin.assert_called_once()

    with subtests.test('delete not called'):
        magic_mock_session.delete.assert_not_called()

    with subtests.test('data returned'):
        assert result is None



