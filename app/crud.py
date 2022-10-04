from sqlalchemy.orm import Session

#import models
#import schemas

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
    else:
        return []


#--- item API -------

def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_tests(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Test).offset(skip).limit(limit).all()

#--- item API -------

def get_orders(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Order).offset(skip).limit(limit).all()


def create_user_order(db: Session, order: schemas.OrderCreate, user_id: int):
    db_order = models.Order(**order.dict(), owner_id=user_id)
    db.add(db_order)
    db.commit()
    db.refresh(db_order)
    return db_order

