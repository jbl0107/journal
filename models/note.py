from sqlalchemy import Integer, String, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class Note(Base):

    __tablename__ = 'notes'

    id:Mapped[int] = mapped_column(Integer, primary_key=True)
    title:Mapped[str] = mapped_column(String(20), nullable=False)
    description:Mapped[str] = mapped_column(String, nullable=False)

    def __repr__(self):
        desc =  self.description[:40]+'...' if len(self.description) > 40  else self.description
        return f'Note(title={self.title}, description={desc})'
    
    __table_args__ = (
        CheckConstraint('char_length(title) >= 2', 'min_title')
    )


