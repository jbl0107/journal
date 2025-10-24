import pytest
from crud.user import get_users, get_user_by_id, create_user, delete_user, update_user
from unittest.mock import Mock, MagicMock
from schemas.user import UserCreate, UserUpdate, UserPatch
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
    '''Mock de SQLAlchemy Session con spec para verificar métodos.'''
    return MagicMock(spec=Session)


@pytest.fixture
def mock_session():
    '''Mock de SQLAlchemy Session'''
    return Mock()

@pytest.fixture
def mock_e_orig():
    '''
    Fixture que simula el atributo `diag` de `e.orig` para una excepción
    de restricción de unicidad en la columna `username`
    '''
    mock_e_orig = Mock()
    mock_e_orig.diag.constraint_name = 'users_username_key'
    return mock_e_orig


@pytest.fixture(params=[
    UserUpdate(first_name='Pepe', last_name='Ruiz', username='nuevo_username', age=25, password='asdfgh123'),
    UserPatch(username='nuevo_username', age=26)
    ], ids=['put', 'patch'])
def user_put_patch(request):
    return request.param

## FIN FIXTURE ##



@pytest.mark.parametrize('users', (
    [],
    [User(id=1, first_name='Pepe', last_name = 'ultimo', username = 'pep_ul', age  = 24, password='123456')],
    [
        User(id=1, first_name='Pepe', last_name = 'ultimo', username = 'pep_ul', age  = 24, password='123456'),
        User(id=2, first_name='Lorem', last_name = 'ipsum', username = 'Manuel', age  = 33, password='123456')
    ]
), ids=['empty', 'single_user_list', 'some_users_list'])
def test_get_users(mock_session, users, subtests):
    '''
    Test unitario que determina si la función crud get_users devuelve 
    los datos correctos, además de comprobar la estructura del SQL
    '''

    mock_scalar_result = Mock()
    mock_scalar_result.all.return_value = users

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
def test_get_user_by_id(mock_session, user, subtests): # subtests -> plugin detectado auto. por pytest como fixture
    '''
    Test que determina si la función crud get_user_by_id devuelve 
    los datos correctos, además de comprobar la estructura del SQL
    '''

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



def test_create_user_error(magic_mock_session, mock_e_orig, user):
    '''
    Test unitario que comprueba el comportamiento de la función CRUD create_user
    cuando se intenta insertar un usuario con un username que ya existe
    (violación de la restricción de unicidad).
    '''

    magic_mock_session.add.side_effect = IntegrityError(None, None, mock_e_orig) # cada vez que alguien llame a add, lanza esta exc

    with pytest.raises(UserAlreadyExists):
        create_user(user, magic_mock_session)


def test_update_user_ok(magic_mock_session, user, user_put_patch, subtests):
    '''Test que valida actualización exitosa (PUT/PATCH) de usuario existente'''
 
    magic_mock_session.get.return_value = user

    user_id = 1
    result = update_user(user_id, user_put_patch, magic_mock_session)

    with subtests.test('data validation'):
        if isinstance(user_put_patch, UserUpdate):
            assert UserUpdate.model_validate(result) == user_put_patch
        else:
            for field in user_put_patch.model_fields_set:
                user_patch = UserPatch.model_validate(result)
                assert getattr(user_patch, field) == getattr(user_put_patch, field)

    with subtests.test('begin called once'):
        magic_mock_session.begin.assert_called_once()

    with subtests.test('get called once with'):
        magic_mock_session.get.assert_called_once_with(User, user_id)   
    


def test_update_user_none(magic_mock_session, user_put_patch, subtests):
    '''Test que valida que update_user devuelve None cuando el usuario no existe'''

    magic_mock_session.get.return_value = None

    user_id = 1
    result = update_user(user_id, user_put_patch, magic_mock_session)

    with subtests.test('begin called once'):
        magic_mock_session.begin.assert_called_once()

    with subtests.test('get called once'):
        magic_mock_session.get.assert_called_once_with(User, user_id)

    with subtests.test('return value'):
        assert result is None


def test_update_user_username_already_exists(magic_mock_session, mock_e_orig, user, user_put_patch, subtests):
    '''Test que valida que update_user lanza UserAlreadyExists con username duplicado'''

    magic_mock_session.get.return_value = user

    # --- Mock del contexto de transacción ---
    # Obtiene el contexto devuelto por `session.begin()` para manipular su comportamiento
    mock_ctx = magic_mock_session.begin.return_value
    def raise_integrity_error(*args, **kwargs):
        raise IntegrityError(None, None, mock_e_orig)

    # Simula que al finalizar el bloque `with session.begin()`
    # SQLAlchemy lanza una `IntegrityError` (por restricción UNIQUE en username)
    mock_ctx.__exit__.side_effect = raise_integrity_error


    with subtests.test('UserAlreadyExists exception'):
        with pytest.raises(UserAlreadyExists):
            update_user(1, user_put_patch, magic_mock_session)

    
    with subtests.test('commit not called'):
        magic_mock_session.commit.assert_not_called()



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
    