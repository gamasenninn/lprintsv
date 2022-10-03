from ast import alias
from typing import Union

from pydantic import BaseModel
from pydantic import Field


class ItemBase(BaseModel):
    title: str
    description: Union[str, None] = None


class ItemCreate(ItemBase):
    pass


class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True


class UserBase(BaseModel):
    email: str


class UserCreate(UserBase):
    password: str
    name: str


class UserUpdate(UserBase):
    name: str
    is_active: bool


class User(UserBase):
    id: int
    name: str
    is_active: bool
    items: list[Item] = []

    class Config:
        orm_mode = True


class TestBase(BaseModel):
    name: str = Field(alias="aname")


class Test(TestBase):
    id: int
    #日本語名前: str  # = Field(alias="日本語名前")
    #日本語住所: str  # = Field(alias="日本語住所")

    class Config:
        orm_mode = True
