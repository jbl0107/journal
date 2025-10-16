from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional


class UserBase(BaseModel):
    first_name:str = Field(min_length=2, max_length=25)
    last_name:str = Field(min_length=2, max_length=30)
    username:str = Field(min_length=3, max_length=20)
    email:Optional[EmailStr] = None
    age:int = Field(gt=0, lt=100)

class UserRead(UserBase):
    id:int
    

class UserUpdate(UserBase):
    first_name:Optional[str] = Field(None, min_length=2, max_length=25)
    last_name:Optional[str] = Field(None, min_length=2, max_length=30)
    username:Optional[str] = Field(None, min_length=3, max_length=20)
    age:Optional[int] = Field(None, gt=0, lt=100)


class UserCreate(UserBase):
    password:str = Field(min_length=8)


class UserInDb(UserRead):
    password:str = Field(min_length=8)
    is_active:bool = True

    model_config = ConfigDict(from_attributes=True) # se le dice a Pydantic que acepte objetos ORM y lea los atributos directamente

    