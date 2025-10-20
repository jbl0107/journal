import pytest
from crud.user import get_users, get_user_by_id, create_user
from unittest.mock import Mock, MagicMock
from schemas.user import UserCreate
from models.user import User
from sqlalchemy.exc import IntegrityError
from exceptions.user_exceptions import UserAlreadyExists
from models.note import Note  # Necesario en runtime para que SQLAlchemy resuelva User.notes
# Aunque la tabla 'notes' ya exista en la base de datos, SQLAlchemy necesita la clase Note
# en memoria al crear el mapper de User. Esto asegura que la relación notes funcione correctamente durante los tests.


## FIXTURE ##
@pytest.fixture
def user():
    return User(first_name='Pepe', last_name = 'Ruiz', username = 'rai17', age  = 24, password='12345678')


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
    mock_session.scalar.return_value = user

    # Cada bloque `with subtests` crea un subtest independiente,
    # permitiendo identificar exactamente qué assert falla sin perder los demás

    with subtests.test('return correct user'):
        assert get_user_by_id(mock_session, 1) == user

    #Comprobar que se llama scalar
    with subtests.test('calls scalar once'):
        mock_session.scalar.assert_called_once()

    # Comprobar que la consulta sql es llamada correctamente
    called_select = mock_session.scalar.call_args.args[0]

    with subtests.test('query selects from correct table'):
        assert called_select.columns_clause_froms[0].name == User.__table__.name

    where = called_select.whereclause

    with subtests.test('where clause filters by id'):
        # Verifica que se filtra por la columna correcta de la tabla (.c devuelve las columnas)
        assert where.left.compare(User.__table__.c.id), 'La columna filtrada no es User.id'
        assert where.right.value == 1  # .right.value contiene el valor del parámetro en el WHERE



def test_create_user_ok(user, subtests):
    '''
    Test unitario que comprueba el funcionamiento de la función CRUD create_user
    en un caso exitoso (inserción correcta de un nuevo usuario).
    '''
    mock_session = MagicMock()
    
    result = create_user(UserCreate.model_validate(user), mock_session)

    called_user:User = mock_session.add.call_args.args[0]

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
        mock_session.add.assert_called_once()

    with subtests.test('begin called once'):
        mock_session.begin.assert_called_once()



def test_create_user_error(user):
    '''
    Test unitario que comprueba el comportamiento de la función CRUD create_user
    cuando se intenta insertar un usuario con un username que ya existe
    (violación de la restricción de unicidad).
    '''

    mock_session = MagicMock()

    mock_e_orig = Mock()
    mock_e_orig.diag.constraint_name = 'users_username_key'
    mock_session.add.side_effect = IntegrityError(None, None, mock_e_orig) # cada vez que alguien llame a add, lanza esta exc

    with pytest.raises(UserAlreadyExists):
        create_user(user, mock_session)


