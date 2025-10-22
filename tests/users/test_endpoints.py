import pytest
from fastapi.testclient import TestClient
from fastapi import status
from unittest.mock import Mock, MagicMock

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from schemas.user import UserRead, UserCreate
from models.user import User

from main import app
from db import get_db

from tests.users.helpers import call_endpoint, assert_422
from tests.users.constants import (
    VALIDATION_TOO_SHORT, VALIDATION_TOO_LONG, 
    VALIDATION_GREATER_THAN, VALIDATION_LESS_THAN, 
    REQUIRED_FIELDS, ASSERT_FIELD_ERRORS,
    BASE_URL, MSG_NO_AT
    )


client = TestClient(app)



### FIXTURES ###
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
    '''
    Fixture que crea una sesión MagicMock para endpoints que dependen de `get_db`.
    - Sobrescribe `get_db` para usar la sesión MagicMock en lugar de la DB real.
    - Solo afecta a este test en memoria y se limpia automáticamente después.
    '''
    magic_mock_session = MagicMock(spec=Session)

    def override_get_db():
        yield magic_mock_session

    app.dependency_overrides[get_db] = override_get_db

    yield magic_mock_session

    app.dependency_overrides.pop(get_db, None)



@pytest.fixture
def magic_mock_session_with_add(magic_mock_session):
    '''
    Fixture que crea una sesión MagicMock para endpoints que dependen de `get_db`
    con el método add definido
    '''

    # Simula que la base de datos asigna un ID al añadir un usuario
    def fake_add(user):
        user.id = 1
        return user
    
    magic_mock_session.add.side_effect = fake_add
    return magic_mock_session


@pytest.fixture(params=[
    [],
    [User(id=1, first_name='Pepe', last_name = 'Rodriguez', username = 'pep_ul', age  = 24)],
    [
        User(id=1, first_name='Pepe', last_name = 'Rodriguez', username = 'pep_ul', age  = 24),
        User(id=2, first_name='Manuel', last_name = 'Quintero', username = 'quintM', age  = 20),
        User(id=3, first_name='Rodrigo', last_name = 'Goes', username = 'rgoes', age  = 25)
    ]
], ids=['empty', 'single_user', 'multiple_users'])
def user_list(mock_db_session, request):
    '''
    Fixture que prepara a la sesión mockeada para que tenga un valor al llamar a su método
    "scalars.all". Se devuelve el resultado para poder utilizarlo en el test correspondiente
    y poder hacer comparaciones
    '''
    mock_db_session.scalars.return_value.all.return_value = request.param
    return request.param


@pytest.fixture(params=[
    User(id=1, first_name='Pepe', last_name = 'Rodriguez', username = 'pep_ul', age  = 24),
    User(id=3, first_name='Rodrigo', last_name = 'Goes', username = 'rgoes', email='rgoes@gmail.com', age  = 25)
], ids=['pep_ul', 'rgoes'])
def user(mock_db_session, request):
    '''
    Fixture que prepara a la sesión mockeada para que tenga un valor al llamar a su metodo
    "get". Se devuelve el resultado para poder utilizarlo en el test correspondiente
    y poder hacer comparaciones
    '''
    mock_db_session.get.return_value = request.param
    return request.param


@pytest.fixture(params=[
    UserCreate(first_name='Pepe', last_name = 'Rodriguez', username = 'pep_ul', age  = 24, password='12345678'),
    UserCreate(first_name='Xi', last_name = 'Li', username = 'liX', age  = 1, email='xi@correo.com', password='12345678'),
    UserCreate(first_name='Antonio Alberto Manuel Le', last_name = 'Montelarguesdevalencierra', username = 'montelarguesdevalenc', age  = 99, password='1278bvhvghf345678')
])
def user_create(request):
    return request.param


@pytest.fixture
def create_response(magic_mock_session_with_add, user_create):
    '''Fixture que crea un usuario vía POST y devuelve el response'''
    return call_endpoint(client=client, method='post', base_url=BASE_URL, payload=user_create.model_dump())


@pytest.fixture
def valid_payload():
    return {
        "first_name": "Pepe",
        "last_name": "Rodriguez",
        "username": "pep_ul",
        "age": 24,
        "password": "12345678"
    }

### FIN FIXTURES ###



## TESTS GET_ALL ##

def test_get_all_users_ok(user_list, subtests):
    '''
    Test básico para asegurar que el endpoint `/users` responde 200 OK.
    Valida que la respuesta contenga exactamente los datos esperados.
    '''
    
    response = call_endpoint(client=client, method='get', base_url=BASE_URL)

    with subtests.test('status code'):
        assert response.status_code == status.HTTP_200_OK

    with subtests.test('data validation'):
        assert response.json() == [UserRead.model_validate(fu).model_dump() for fu in user_list]
    


## TESTS GET_BY_ID ##

def test_get_by_id_ok(user, subtests):
    '''
    Test unitario básico para validar que el endpoint get_by_id responde 200 OK
    cuando el usuario con el id especificado existe, además de validar los datos
    '''
    response = call_endpoint(client=client, method='get_by_id', base_url=BASE_URL, resource_id=user.id)
    with subtests.test('status code'):
        assert response.status_code == status.HTTP_200_OK

    with subtests.test('data validation'):
        assert response.json() == UserRead.model_validate(user).model_dump()


def test_get_by_id_not_found(mock_db_session):
    '''
    Test unitario básico para validar que el endpoint get_by_id responde 404 NOT FOUND
    cuando no existe el usuario con el id especificado
    '''
    mock_db_session.get.return_value = None
    response = call_endpoint(client=client, method='get_by_id', base_url=BASE_URL, resource_id=110)
    assert response.status_code == status.HTTP_404_NOT_FOUND



## TESTS CREATE ##

def test_create_ok(create_response, user_create, subtests):
    '''
    Test unitario básico para validar que el endpoint create responde 201
    cuando el usuario ha sido creado y que los datos devueltos son correctos
    '''

    with subtests.test('status code'):
        assert create_response.status_code == status.HTTP_201_CREATED


    data = create_response.json()
    user_out = UserRead.model_validate(data).model_dump(exclude={'id'})

    with subtests.test('data validation'):
        assert user_create.model_dump(exclude={'password'}) == user_out



## TESTS UPDATE ##

def test_update_ok(magic_mock_session, valid_payload):
    pass



## TESTS VALIDATION FOR CREATE / UPDATE ##

def test_create_username_exist_error(magic_mock_session_with_add, user_create):
    '''
    Test unitario que valida si el endpoint create devuelve un 400
    cuando se intenta insertar un usuario con un username ya existente
    '''

    mock_e_orig = Mock()
    mock_e_orig.diag.constraint_name = 'users_username_key'
    magic_mock_session_with_add.add.side_effect = IntegrityError(None, None, mock_e_orig)

    response = call_endpoint(client=client, method='post', base_url=BASE_URL, payload=user_create.model_dump())

    assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.parametrize('field', ['first_name', 'last_name', 'username', 'age', 'password'], 
                         ids=['first_name missing', 'last_name missing', 'username missing', 'age missing', 'password missing'])
def test_create_required_fields_missing(magic_mock_session, valid_payload, field, subtests):
    '''
    Test unitario que valida si el endpoint devuelve un error
    422 cuando se intenta pasar un payload sin algún campo obligatorio
    '''
    valid_payload.pop(field)
    response = call_endpoint(client=client, method='post', base_url=BASE_URL, payload=valid_payload)

    assert_422(response, subtests, context=REQUIRED_FIELDS, field=field)


@pytest.mark.parametrize(['field', 'value', 'msg'], [
    ('first_name', 'a', VALIDATION_TOO_SHORT),
    ('first_name', 'a'*26, VALIDATION_TOO_LONG),
    ('first_name', '', VALIDATION_TOO_SHORT),
    ('last_name', 'b', VALIDATION_TOO_SHORT),
    ('last_name', 'b'*31, VALIDATION_TOO_LONG),
    ('last_name', '', VALIDATION_TOO_SHORT)

], ids=['min first_name', 'max first_name', 'empty first_name', 'min last_name', 'max last_name', 'empty last_name'])
def test_create_name_length_limits(magic_mock_session, valid_payload, subtests, field, value, msg):
    '''
    Test unitario que intenta crear un usuario con valores límite 
    incorrectos (longitud) en los campos first_name y last_name
    '''
    
    valid_payload[field] = value
    response = call_endpoint(client=client, method='post', base_url=BASE_URL, payload=valid_payload)

    assert_422(response, subtests, context=ASSERT_FIELD_ERRORS, field=field, msg=msg)



@pytest.mark.parametrize(['value', 'msg'], [
    ('us', VALIDATION_TOO_SHORT),
    ('', VALIDATION_TOO_SHORT),
    (' ', VALIDATION_TOO_SHORT),
    ('a'*21, VALIDATION_TOO_LONG)

], ids=['min username', 'empty username', 'only_one_space', 'max username'])
def test_create_username_limits(magic_mock_session, valid_payload, subtests, value, msg):
    '''
    Test unitario que intenta crear un usuario con
    valores incorrectos para el campo username (valores límite de longitud)
    '''

    valid_payload['username'] = value
    response = call_endpoint(client=client, method='post', base_url=BASE_URL, payload=valid_payload)

    assert_422(response, subtests, context=ASSERT_FIELD_ERRORS, field='username', msg=msg)
    

@pytest.mark.parametrize('value', ['   ', 'user name', ' username', 'username '], 
                         ids=['only_spaces', 'space_in_the_middle', 'begin_with_space', 'end_with_space'])
def test_create_username_regexp(magic_mock_session, valid_payload, subtests, value):
    '''
    Test unitario que intenta crear un usuario con
    un username que no cumple el formato (no se admiten espacios en blanco) 
    '''    
    valid_payload['username'] = value
    response = call_endpoint(client=client, method='post', base_url=BASE_URL, payload=valid_payload)

    assert_422(response, subtests, context=ASSERT_FIELD_ERRORS, field='username', msg='string_pattern_mismatch', 
               label='username regexp')

      

@pytest.mark.parametrize(['value', 'msg'], [
    (0, VALIDATION_GREATER_THAN),
    (-5, VALIDATION_GREATER_THAN),
    (100, VALIDATION_LESS_THAN)
], ids=['0', '-5', '100'])
def test_create_age_range(magic_mock_session, valid_payload, subtests, value, msg):
    '''
    Test unitario que intenta crear un usuario con una edad
    fuera del rango válido [1, 99]
    '''

    valid_payload['age'] = value
    response = call_endpoint(client=client, method='post', base_url=BASE_URL, payload=valid_payload)

    assert_422(response, subtests, context=ASSERT_FIELD_ERRORS, field='age', msg=msg, label='age range')


@pytest.mark.parametrize('value', ['', 'asdfghj', 'as df'], ids=['empty', 'seven characters', 'four characters'])
def test_create_password_length(magic_mock_session, valid_payload, subtests, value):
    '''
    Test unitario que intenta crear un usuario con una contraseña
    que tiene una longitud inferior a la mínima exigida
    '''

    valid_payload['password'] = value
    response = call_endpoint(client=client, method='post', base_url=BASE_URL, payload=valid_payload)

    assert_422(response, subtests, context=ASSERT_FIELD_ERRORS, field='password', msg='string_too_short')


@pytest.mark.parametrize(['value', 'msg'], [
    ('', MSG_NO_AT),
    ('  ', MSG_NO_AT),
    ('sdfdasfe', MSG_NO_AT),
    ('email.com', MSG_NO_AT),
    ('email@.com', 'value is not a valid email address: An email address cannot have a period immediately after the @-sign.'),
    ('email@hotmail. com', 'value is not a valid email address: The part after the @-sign contains invalid characters: SPACE.'),
    ('em ail@mail.com', 'value is not a valid email address: The email address contains invalid characters before the @-sign: SPACE.'),
    ('asdf@-mail.com', 'value is not a valid email address: An email address cannot have a hyphen immediately after the @-sign.')

], ids=['empty email', 'only scapes', 'only letters', 'only characters', '@.', 'space after @', 'space before @', 'invalid character after @'])
def test_create_invalid_email(magic_mock_session, valid_payload, subtests, value, msg):
    ''' Test unitario que intenta crear un usuario con un email inválido '''

    valid_payload['email'] = value
    response = call_endpoint(client=client, method='post', base_url=BASE_URL, payload=valid_payload)

    assert_422(response, subtests, context=ASSERT_FIELD_ERRORS, field='email', msg=msg, label='invalid email', key='msg')
    


## TESTS DELETE ##

def test_delete_ok(magic_mock_session):
    '''Test básico para asegurar que el endpoint `/users/{id}` responde 204 OK'''

    magic_mock_session.get.return_value = User(first_name='Pepe', last_name = 'Ruiz', username = 'rai17', age  = 24, password='12345678')
    response = call_endpoint(client=client, method='delete', base_url=BASE_URL, resource_id=1)

    assert response.status_code == status.HTTP_204_NO_CONTENT
        
    
def test_delete_not_found(magic_mock_session):
    '''
    Test básico para asegurar que el endpoint `/users/{id}` responde 404 en caso
    de que el usuario con dicho ID no exista en el sistema
    '''
    magic_mock_session.get.return_value = None
    
    response = call_endpoint(client=client, method='delete', base_url=BASE_URL, resource_id=100)
    assert response.status_code == status.HTTP_404_NOT_FOUND

