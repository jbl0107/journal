from sqlalchemy import select
from sqlalchemy.orm import Session
from models.user import User #


def get_users(session:Session) -> list[User]:
    return session.scalars(select(User)).all()


def get_user_by_id(session:Session, id:int) -> User | None:
    return session.scalar(select(User).where(User.id == id))
    