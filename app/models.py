#from ast import alias
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Date,DateTime,DATETIME,FetchedValue
from sqlalchemy.orm import relationship
from datetime import datetime

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    name = Column(String, default='')
    is_active = Column(Boolean, default=True)
    created_at = Column(DATETIME, default=datetime.now)
    updated_at = Column(DATETIME, default=datetime.now, onupdate=datetime.now)

    items = relationship("Item", back_populates="owner")
    orders = relationship("Order", back_populates="owner")

class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User", back_populates="items")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    scode = Column(String, index=True)
    title = Column(String)
    in_date = Column(Date,default=None)
    person = Column(String)
    memo = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DATETIME, default=datetime.now)
    updated_at = Column(DATETIME, default=datetime.now, onupdate=datetime.now)

    owner = relationship("User", back_populates="orders")


class Test(Base):
    __tablename__ = "tests"

    id = Column(Integer, primary_key=True, index=True)
    aname = Column(String, default='')
