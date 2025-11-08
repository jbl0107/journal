from db import get_db
from schemas.note import NoteRead, NoteCreate, NoteUpdate, NotePatch
from repositories.note import get_all, get_by_id, create, update, delete
from exceptions.note_exceptions import UserNotFound

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

router = APIRouter(prefix='/notes', tags=['Notes'])

@router.get('/')
def get_notes(session:Session = Depends(get_db)) -> list[NoteRead]:
    '''Devuelve todas las notas creadas por los usuarios'''
    return get_all(session)


@router.get('/{id}', responses={
    404:{'description':'La nota con id especificado no existe'}
})
def get_note(id:int, session:Session = Depends(get_db)) -> NoteRead:
    '''Recupera la información de una nota específica'''
    note = get_by_id(session, id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='La nota con id especificado no existe')
    
    return note


@router.post('/', status_code=status.HTTP_201_CREATED, responses={
    400:{'description':'El usuario con id especificado no existe'}
})
def create_note(note_create: NoteCreate, session: Session = Depends(get_db)) -> NoteRead:
    '''Crea una nueva nota en el sistema'''

    try:
        return create(session, note_create)

    except UserNotFound as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
    

@router.put('/{id}', responses={
    404:{'description': 'La nota con id especificado no existe'}
})
def update_note(id:int, note_put: NoteUpdate, session:Session = Depends(get_db)) -> NoteRead:
    '''Actualiza una nota del sistema'''

    return _handle_update(id, note_put, session)


@router.patch('/{id}', responses={
    404:{'description': 'La nota con id especificado no existe'}
})
def partial_update_note(id:int, note_patch:NotePatch, session:Session = Depends(get_db)) -> NoteRead:
    '''Actualiza una nota del sistema parcialmente'''

    return _handle_update(id, note_patch, session)
    

@router.delete('/{id}', status_code=status.HTTP_204_NO_CONTENT, responses={
    404:{'description': 'La nota con id especificado no existe'}
})
def delete_note(id, session:Session = Depends(get_db)) -> None:
    '''Elimina una nota del sistema'''

    note = delete(session, id)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='La nota con id especificado no existe')
    





def _handle_update(note_id:int, note_update: NoteUpdate | NotePatch, session:Session) -> NoteRead:
    note = update(session, note_id, note_update)
    if note is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='La nota con id especificado no existe')
    
    return note