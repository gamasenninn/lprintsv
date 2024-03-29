from sqlalchemy.orm import Session
from sqlalchemy import desc

import models
import schemas

#--- user API -------
def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(
        email=user.email, 
        hashed_password=fake_hashed_password,
        name=user.name
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(user_id: int, db: Session, user: schemas.UserUpdate):
    db_user = db.query(models.User).filter(models.User.id == user_id).first()
    if db_user:
        db_user.email=user.email 
        db_user.name=user.name
        #db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    #else:
    #    return []


#--- item API -------

def get_items(db: Session, skip: int = 0, limit: int = 100):

    items = db.query(models.Item).offset(skip).limit(limit).all()
    for item in items: 
        print("items:",item.owner.name)
    return items

def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


#def get_tests(db: Session, skip: int = 0, limit: int = 100):
#    return db.query(models.Test).offset(skip).limit(limit).all()

#--- Order API -------

def get_orders(db: Session, skip: int = 0, limit: int = 100, gte: int = 0,scode: str='',place=''):

    if place:
        return (
            db.query(models.Order)
            .filter(models.Order.stock_qty >= gte)
            .filter(models.Order.scode.contains(scode))
            .filter(models.Order.place.contains(place))
            .order_by(desc(models.Order.id))
            .offset(skip).limit(limit)
            .all())
    else:
        return (
            db.query(models.Order)
            .filter(models.Order.stock_qty >= gte)
            .filter(models.Order.scode.contains(scode))
            .order_by(desc(models.Order.id))
            .offset(skip).limit(limit)
            .all())



def get_orders_by_id(db: Session, order_id: int):
    return db.query(models.Order).filter(models.Order.id == order_id).first()

def create_user_order(db: Session, order: schemas.OrderCreate, user_id: int):
    db_order = models.Order(**order.dict(), owner_id=user_id)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

def update_order(db: Session, order: schemas.OrderUpdate, id: int):
    db_order = db.query(models.Order).filter(models.Order.id == id).first()
    if db_order:

        #db_order.scode=order.scode
        #db_order.title=order.title
        #db_order.receipt_date=order.receipt_date
        #db_order.person=order.person
        #db_order.memo=order.memo
        #db_order.status=order.status

        attributes = ['scode', 'title', 'receipt_date', 'person', 'memo', 'status']

        for attr in attributes:
            new_value = getattr(order, attr)
            if new_value is not None:
                setattr(db_order, attr, new_value)

        db.commit()
        db.refresh(db_order)
        return db_order

def delete_order(db: Session,  id: int):
    db_order = db.query(models.Order).filter(models.Order.id == id).first()
    if db_order:
        db.delete(db_order)
        db.commit()
        return {"result":"ok"}
