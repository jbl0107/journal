from pydantic import BaseModel, Field
from typing import Optional
from .user import UserRead


class NoteBase(BaseModel):
    title:str = Field(min_length=2, max_length=20)
    description:str


class NoteRead(NoteBase):
    user: UserRead


class NoteCreate(NoteBase):
    user_id:int

class NoteUpdate(BaseModel):
    title:Optional[str] = Field(None, max_length=20)
    description:Optional[str] = None


class NoteDb(NoteCreate):
    id:int

    class Config:
        orm_mode = True