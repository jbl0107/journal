from db import get_db
from schemas.note import NoteRead, NoteCreate, NoteUpdate, NotePatch
from crud.note import get_notes, get_note_by_id, create_note, update_note
from exceptions.note_exceptions import UserNotFound

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix='/notes', tags=['Notes'])

@router.get('/')
def get_all(session:Session = Depends(get_db)) -> list[NoteRead]:
    '''Devuelve todas las notas creadas por los usuarios'''
    return get_notes(session)


@router.get('/{note_id}', responses={
    404:{'description':'La nota con id especificado no existe'}
})
def get_by_id(note_id:int, session:Session = Depends(get_db)) -> NoteRead:
    '''Recupera la información de una nota específica'''
    note = get_note_by_id(session, note_id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='La nota con id especificado no existe')
    
    return note


@router.post('/', status_code=status.HTTP_201_CREATED, responses={
    400:{'description':'El usuario con id especificado no existe'}
})
def create(note_create: NoteCreate, session: Session = Depends(get_db)) -> NoteRead:
    '''Crea una nueva nota en el sistema'''

    try:
        return create_note(session, note_create)

    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    

@router.put('/{note_id}', responses={
    404:{'description': 'La nota con id especificado no existe'}
})
def put(note_id:int, note_put: NoteUpdate, session:Session = Depends(get_db)) -> NoteRead:
    '''Actualiza una nota del sistema'''

    return _handle_update(note_id, note_put, session)


@router.patch('/{note_id}', responses={
    404:{'description': 'La nota con id especificado no existe'}
})
def patch(note_id:int, note_patch:NotePatch, session:Session = Depends(get_db)) -> NoteRead:
    '''Actualiza una nota del sistema parcialmente'''

    return _handle_update(note_id, note_patch, session)
    





def _handle_update(note_id:int, note_update: NoteUpdate | NotePatch, session:Session) -> NoteRead:
    note = update_note(session, note_id, note_update)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='La nota con id especificado no existe')
    
    return note