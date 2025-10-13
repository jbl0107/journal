from pydantic import BaseModel, Field, EmailStr
from typing import Optional

class UserRead(BaseModel):
    first_name:str = Field(min_length=2, max_length=25)
    last_name:str = Field(min_length=2, max_length=30)
    username:str = Field(min_length=3, max_length=20)
    email:Optional[EmailStr] = None
    age:int = Field(gt=0, lt=100)


class UserUpdate(BaseModel):
    first_name:Optional[str] = Field(None, min_length=2, max_length=25)
    last_name:Optional[str] = Field(None, min_length=2, max_length=30)
    username:Optional[str] = Field(None, min_length=3, max_length=20)
    email:Optional[EmailStr] = None
    age:Optional[int] = Field(None, gt=0, lt=100)


class UserCreate(UserRead):
    password:str = Field(min_length=8)


class UserDb(UserCreate):
    id:int
    is_active:bool = True

    class Config:
        orm_mode = True # se le dice a Pydantic que acepte objetos ORM y lea los atributos directamente

    