from fastapi import APIRouter, Depends
from crud.user import get_users
from schemas.user import UserRead
from sqlalchemy.orm import Session
from db import get_db

router = APIRouter(prefix='/users', tags=['Users'])


@router.get('/')
def get_all(db: Session = Depends(get_db)) -> list[UserRead]:
    return get_users(db)



