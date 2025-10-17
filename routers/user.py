from fastapi import APIRouter, Depends, status, HTTPException
from crud.user import get_users, get_user_by_id
from schemas.user import UserRead, UserCreate
from sqlalchemy.orm import Session
from db import get_db

router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/')
def get_all(db: Session = Depends(get_db)) -> list[UserRead]:
    return get_users(db)


@router.get('/{id}')
def get_by_id(id:int, db:Session = Depends(get_db)) -> UserRead:
    user = get_user_by_id(db, id)
    if user:
        return user
    
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='El usuario con id especificado no existe')

