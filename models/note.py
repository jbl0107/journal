from __future__ import annotations

from sqlalchemy import Integer, String, CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .user import User

class Note(Base):

    __tablename__ = 'notes'

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    title:Mapped[str] = mapped_column(String(20), nullable=False)
    description:Mapped[str] = mapped_column(String(150), nullable=False)
    user_id:Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))

    user:Mapped[User] = relationship(back_populates="notes")

    def __repr__(self):
        desc =  self.description[:40]+'...' if len(self.description) > 40  else self.description
        return f'Note(title={self.title}, description={desc})'
    
    __table_args__ = (
        CheckConstraint('char_length(title) >= 2', 'min_title'),
        CheckConstraint('char_length(description) >= 5', 'min_des')
    )


