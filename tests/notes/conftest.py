from models.user import User

import pytest

@pytest.fixture
def user_pepe():
    """Usuario base reutilizable."""
    return User(
        id=1,
        first_name='Pepe',
        last_name='Rodriguez',
        username='pep_ul',
        age=24
    )