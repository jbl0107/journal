from sqlalchemy import Integer, String, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base #el . (importacion relativa) es igual a paquete actual. Python sabe que debe buscar dentro de models/
from typing import Optional


class User(Base):
    __tablename__ = 'users'

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    first_name:Mapped[str] = mapped_column(String(25), nullable=False)
    last_name:Mapped[str] = mapped_column(String(30), nullable=False)
    username:Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    email:Mapped[Optional[str]] = mapped_column(String, nullable=True)
    age:Mapped[int] = mapped_column(Integer, nullable=False)
    password:Mapped[str] = mapped_column(String, nullable=False)
    is_active:Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)


    #metodo que define como se ve en consola el objeto al imprimirlo o inspeccionarlo
    def __repr__(self):
        return f'User(id={self.id}, first_name={self.first_name}, last_name={self.last_name}, username={self.username})'


    __table_args__ = (
        CheckConstraint('age > 0 AND age < 100', 'age_range'),
        CheckConstraint('char_length(password) >= 8', 'password_min_length'),
        CheckConstraint('char_length(first_name) >= 2', 'first_name_min_length'),
        CheckConstraint('char_length(last_name) >= 2', 'last_name_min_length'),
        CheckConstraint('char_length(username) >= 3', 'username_min_length')
    )