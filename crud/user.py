from sqlalchemy import select
from sqlalchemy.orm import Session
from models.user import User


def get_users(session:Session):
    return session.scalars(select(User)).all()

