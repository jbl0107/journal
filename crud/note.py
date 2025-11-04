from models.note import Note
from schemas.note import NoteCreate

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
    new_note = Note(**note.model_dump())

    with session.begin():
        session.add(new_note)

    return new_note
