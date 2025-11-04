from db import get_db
from schemas.note import NoteRead
from crud.note import get_notes, get_note_by_id

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix='/notes', tags=['Notes'])

@router.get('/')
def get_all(session:Session = Depends(get_db)) -> list[NoteRead]:
    '''Devuelve todas las notas creadas por los usuarios'''
    return get_notes(session)


@router.get('/{id}', responses={
    404:{'description':'La nota con id especificado no existe'}
})
def get_by_id(id:int, session:Session = Depends(get_db)) -> NoteRead:
    '''Recupera la información de una nota específica'''
    note = get_note_by_id(session, id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='La nota con id especificado no existe')
    
    return note