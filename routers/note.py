from db import get_db
from schemas.note import NoteRead
from crud.note import get_notes

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

router = APIRouter(prefix='/notes', tags=['Notes'])

@router.get('/')
def get_all(session:Session = Depends(get_db)) -> list[NoteRead]:
    '''Devuelve todas las notas creadas por los usuarios'''
    return get_notes(session)