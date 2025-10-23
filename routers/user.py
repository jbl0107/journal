from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.orm import Session

from crud.user import get_users, get_user_by_id, create_user, delete_user, update_user
from schemas.user import UserRead, UserCreate, UserUpdate, UserPatch
from db import get_db
from exceptions.user_exceptions import UserAlreadyExists


router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/')
def get_all(db: Session = Depends(get_db)) -> list[UserRead]:
    '''Obtiene todos los usuarios registrados'''
    return get_users(db)


@router.get('/{id}', responses={
    404: {'description': 'El usuario con id especificado no existe'}
})
def get_by_id(id:int, db:Session = Depends(get_db)) -> UserRead: 
    '''Recupera la información de un usuario específico'''

    user = get_user_by_id(db, id)
    if user:
        return user
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='El usuario con id especificado no existe')


@router.post('/', status_code=status.HTTP_201_CREATED, responses={
    400: {'description': 'El usuario con el username especificado ya existe'}
})
def create(user:UserCreate, db:Session = Depends(get_db)) -> UserRead:
    ''' Crea un nuevo usuario en el sistema'''

    try:
        return create_user(user, db)

    except UserAlreadyExists as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    

@router.put('/{id}', responses={
    400: {'description': 'El usuario con el username especificado ya existe'},
    404: {'description':'El usuario con id especificado no existe'}
})
def put(id:int, user_update:UserUpdate, session: Session = Depends(get_db)) -> UserRead:
    '''Actualiza un usuario del sistema'''
    return _handle_update(id, user_update, session)


@router.patch('/{id}', responses= {
    400: {'description': 'El usuario con el username especificado ya existe'},
    404: {'description':'El usuario con id especificado no existe'}
})
def patch(id:int, user_patch:UserPatch, session:Session = Depends(get_db)) -> UserRead:
    '''Actualiza un usuario del sistema parcialmente'''
    return _handle_update(id, user_patch, session)
    

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT, responses={
        404: {"description": "El usuario con id especificado no existe"}
    }
)
def delete(id:int, session:Session = Depends(get_db)) -> None:
    '''Elimina un usuario del sistema'''
    user = delete_user(session, id)

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='El usuario con id especificado no existe')
  
        


def _handle_update(id:int, user:UserUpdate | UserPatch, session:Session):
    try:
        user_updated = update_user(id, user, session)
    
    except UserAlreadyExists as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)

    if not user_updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='El usuario con id especificado no existe')
    

    return user_updated