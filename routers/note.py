from db import get_db
from schemas.note import NoteRead, NoteCreate
from crud.note import get_notes, get_note_by_id, create_note
from exceptions.note_exceptions import UserNotFound

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


@router.post('/', status_code=status.HTTP_201_CREATED, responses={
    404:{'description':'El usuario con id especificado no existe'}
})
def create(note_create: NoteCreate, session: Session = Depends(get_db)) -> NoteRead:
    '''Crea una nueva nota en el sistema'''

    try:
        return create_note(session, note_create)

    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=e.message)
    