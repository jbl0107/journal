from fastapi import APIRouter, Depends, status, HTTPException
from crud.user import get_users, get_user_by_id, create_user
from schemas.user import UserRead, UserCreate
from sqlalchemy.orm import Session
from db import get_db
from exceptions.user_exceptions import UserAlreadyExists


router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/')
def get_all(db: Session = Depends(get_db)) -> list[UserRead]:
    '''Endpoint para obtener todos los usuarios'''
    return get_users(db)


@router.get('/{id}')
def get_by_id(id:int, db:Session = Depends(get_db)) -> UserRead: 
    '''Endpoint para obtener un usuario por id'''

    user = get_user_by_id(db, id)
    if user:
        return user
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='El usuario con id especificado no existe')


@router.post('/', status_code=status.HTTP_201_CREATED)
def create(user:UserCreate, db:Session = Depends(get_db)) -> UserRead:
    '''Ednpoint para crear un usuario'''

    try:
        return create_user(user, db)

    except UserAlreadyExists as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    
  
        
