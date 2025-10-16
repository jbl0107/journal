from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from .user import UserRead


class NoteBase(BaseModel):
    title:str = Field(min_length=2, max_length=20)
    description:str = Field(min_length=5, max_length=150)


class NoteRead(NoteBase):
    id:int
    user: UserRead


class NoteCreate(NoteBase):
    user_id:int

class NoteUpdate(NoteBase):
    title:Optional[str] = Field(None, max_length=20)
    description:Optional[str] = Field(None, min_length=5, max_length=150)


class NoteInDb(NoteCreate):
    id:int
    model_config = ConfigDict(from_attributes=True)