import pytest
from crud.user import get_users, get_user_by_id
from unittest.mock import Mock
from models.user import User
from models.note import Note  # Necesario en runtime para que SQLAlchemy resuelva User.notes
# Aunque la tabla 'notes' ya exista en la base de datos, SQLAlchemy necesita la clase Note
# en memoria al crear el mapper de User. Esto asegura que la relación notes funcione correctamente durante los tests.



@pytest.mark.parametrize('users', (
    [],
    [User(id=1, first_name='Pepe', last_name = 'ultimo', username = 'pep_ul', age  = 24, password='123456')],
    [
        User(id=1, first_name='Pepe', last_name = 'ultimo', username = 'pep_ul', age  = 24, password='123456'),
        User(id=2, first_name='Lorem', last_name = 'ipsum', username = 'Manuel', age  = 33, password='123456')
    ]
), ids=['empty', 'single_user_list', 'some_users_list'])
def test_get_users(users):

    mock_scalar_result = Mock()
    mock_scalar_result.all.return_value = users

    mock_session = Mock()
    mock_session.scalars.return_value = mock_scalar_result


    result = get_users(mock_session)

    assert result == users

    mock_session.scalars.assert_called_once()
    mock_scalar_result.all.assert_called_once()



@pytest.mark.parametrize('user', (
        User(id=1, first_name='Pepe', last_name = 'ultimo', username = 'pep_ul', age  = 24, password='123456'),
        None
), ids=['user', 'None'])
def test_get_user_by_id(user):
    mock_session = Mock()
    mock_session.scalar.return_value = user

    assert get_user_by_id(mock_session, 1) == user

    mock_session.scalar.assert_called_once()


