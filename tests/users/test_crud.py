import pytest
from crud.user import get_users 
from unittest.mock import Mock

def test_get_users():
    fake_user = Mock(id=1, first_name='Jesus')

    mock_scalar_result = Mock()
    mock_scalar_result.all.return_value = [fake_user]

    mock_session = Mock()
    mock_session.scalars.return_value = mock_scalar_result


    result = get_users(mock_session)

    assert result == [fake_user]

    mock_session.scalars.assert_called_once()
    mock_scalar_result.all.assert_called_once()