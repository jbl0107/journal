from sqlalchemy import select, insert
from sqlalchemy.orm import Session
from models.user import User
from sqlalchemy.exc import IntegrityError
from schemas.user import UserCreate
from exceptions.user_exceptions import UserAlreadyExists


def get_users(session:Session) -> list[User]:
    '''Operación CRUD que obtiene todos los usuarios'''
    return session.scalars(select(User)).all()


def get_user_by_id(session:Session, id:int) -> User | None:
    '''
    Operación CRUD que obtiene el usuario especificado por el parámetro id.
    Si no existe en BD, devuelve None
    '''
    return session.scalar(select(User).where(User.id == id))
    

def create_user(user: UserCreate, session:Session) -> User:
    '''
    Operación CRUD que inserta un registro en la tabla de Usuario.
    Posibles excepciones:
    - UserAlreadyExists -> Ya existe un usuario con ese username en BD
    '''

    new_user = User(first_name=user.first_name, last_name=user.last_name, username=user.username,
                                                email=user.email, age=user.age, password=user.password)
    try:
        with session.begin():
            session.add(new_user)

    except IntegrityError as e:
        # asi da igual idioma, version de librerias, etc. Siempre devolverá el mismo nombre
        constraint = getattr(e.orig.diag, 'constraint_name', None) 
        if constraint == 'users_username_key': 
            raise UserAlreadyExists(username=user.username)
        
        raise # Relanzar cualquier excepcion no contemplada
    
    return new_user