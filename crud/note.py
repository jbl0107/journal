from models.note import Note

from sqlalchemy import select
from sqlalchemy.orm import Session


def get_notes(session:Session) -> list[Note]:
    ''' Operación CRUD que obtiene todos los usuarios'''
    return session.scalars(select(Note)).all()


def get_note_by_id(id:int, session:Session) -> Note | None:
    '''
    Operación CRUD que devuelve la Note con id especificado.
    Si no existe, devuelve None
    '''
    return session.get(Note, id)