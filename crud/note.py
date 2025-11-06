from models.note import Note
from models.user import User
from schemas.note import NoteCreate, NoteUpdate, NotePatch
from exceptions.note_exceptions import UserNotFound

from sqlalchemy import select
from sqlalchemy.orm import Session


def get_notes(session:Session) -> list[Note]:
    ''' Operación CRUD que obtiene todos los usuarios'''
    return session.scalars(select(Note)).all()


def get_note_by_id(session:Session, id:int) -> Note | None:
    '''
    Operación CRUD que devuelve la Note con id especificado.
    Si no existe, devuelve None
    '''
    return session.get(Note, id)


def create_note(session:Session, note: NoteCreate) -> Note:
    '''
    Operación CRUD que inserta un registro en la tabla Note
    '''

    with session.begin():
        user = session.get(User, note.user_id)
        if user is None:
            raise UserNotFound(note.user_id)
        
        new_note = Note(**note.model_dump())

        session.add(new_note)


    return new_note


def update_note(session:Session, id:int, note_update: NoteUpdate | NotePatch) -> Note:
    '''
    Operación CRUD que actualiza una Note (PUT/PATCH)
    '''

    with session.begin():
        note = session.get(Note, id)
        if note is None:
            return None
        
        for field in note_update.model_fields_set:
            setattr(note, field, getattr(note_update, field))

        
    return note



