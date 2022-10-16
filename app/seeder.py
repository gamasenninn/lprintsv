from datetime import date
from database import SessionLocal
from models import Order, User
#import models
import sys
import argparse
from sqlalchemy.orm import Session

def make_users(db:Session,v):
    users = [
        User(
            id = 1,
            email = "test1@xample.com",
            name = "小野 哲",
            hashed_password = "password01",
            is_active = True,        
        ),
        User(
            id = 2,
            email = "test2@xample.com",
            name = "田中 太郎",
            hashed_password = "password01",
            is_active = True,        
        ),
    ]
    db.add_all(users)
    db.commit()
    users = db.query(User).all()
    if v:
        print('-----User-----')
        for user in users:
            print(user.name)

def make_orders(db:Session,v):

    orders = [
        Order(
            id = 1,
            scode = "12345-1",
            title = "クボタ コンバイン2条刈",
            person = "田中",
            memo = 'メモ01',
            owner_id = 1,
            receipt_date = date(2021,10,1)
        ),
        Order(
            id = 2,
            scode = "23456-1",
            title = "イセキ トラクター 30馬力",
            person = "佐藤",
            memo = 'メモ02',
            owner_id = 1,
            receipt_date = date(2021,10,1)
        ),
        Order(
            id = 3,
            scode = "34567-1",
            title = "ヤンマー　田植機 3条植",
            person = "小野",
            memo = 'メモ03',
            owner_id = 2,
            receipt_date = date(2021,10,1)
        ),
        Order(
            id = 4,
            scode = "45678-1",
            title = "イセキ トラクター 30馬力",
            person = "斎藤",
            memo = 'メモ04',
            owner_id = 2,
            receipt_date = date(2021,10,1)
        ),
    ]
    
    db.add_all(orders)
    db.commit()
    orders = db.query(Order).all()
    if v:
        print('-----Order-----')
        for order in orders:
            print(order.scode)

def seeder(v=False):

    db = SessionLocal()

    models = [
        User,
        Order
    ]

    for model in models:
        db.query(model).delete()
        db.commit()


    make_users(db,v)
    make_orders(db,v)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='seeder -- makeing test data for label print server')
    parser.add_argument('-v', '--verbose',
                        help='output data', action='store_true')
    args = parser.parse_args()

    seeder(v=args.verbose)
