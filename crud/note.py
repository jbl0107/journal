from models.note import Note

from sqlalchemy import select
from sqlalchemy.orm import Session


def get_notes(session:Session) -> list[Note]:
    ''' Operación CRUD que obtiene todos los usuarios'''
    return session.scalars(select(Note)).all()