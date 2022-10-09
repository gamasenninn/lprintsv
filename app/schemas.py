#from ast import alias
from datetime import datetime,date
from typing import Union,List,Optional
#from xmlrpc.client import DateTime

from pydantic import BaseModel
from pydantic import Field

import datetime


#-------- Item ---------------------
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

#------ Oder --------
class OrderBase(BaseModel):
    scode: str
    title: Union[str, None] = None
    in_date: Union[datetime.date,None] = None
    person: Union[str, None] = None
    memo : Union[str, None] = None


class OrderCreate(OrderBase):
    pass
class OrderUpdate(OrderBase):
    pass

class Order(OrderBase):
    id: int
    owner_id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        orm_mode = True

#------ User --------
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
    created_at: datetime.datetime
    updated_at: datetime.datetime
    items: list[Item] = []
    orders: list[Order] = []

    class Config:
        orm_mode = True



#---- Test
class TestBase(BaseModel):
    name: str = Field(alias="aname")


class Test(TestBase):
    id: int
    #日本語名前: str  # = Field(alias="日本語名前")
    #日本語住所: str  # = Field(alias="日本語住所")

    class Config:
        orm_mode = True


