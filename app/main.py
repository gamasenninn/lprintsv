from fastapi import Depends, FastAPI, HTTPException
from fastapi import Body,Response
from sqlalchemy.orm import Session
import crud
import models
import schemas
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
import tpcl_maker.tpcl_maker as tpcl
from convert.load_mysql_orm_view import convert_db

#models.Base.metadata.create_all(bind=engine)

app = FastAPI()
#CORSを有効にする
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


#------ user API -------
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.put("/users/{user_id}", response_model=schemas.User)
def update_user(user_id: int, user: schemas.UserUpdate,db: Session = Depends(get_db)):
    db_user = crud.update_user(user_id=user_id, db=db, user=user)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user
 
#--------- items ------------
@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
    ):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=list[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items

#--------- orders ------------
@app.post("/users/{user_id}/orders/", response_model=schemas.Order)
def create_order_for_user(
    user_id: int, order: schemas.OrderCreate, db: Session = Depends(get_db)
    ):
    return crud.create_user_order(db=db, order=order, user_id=user_id)

@app.put("/orders/{id}", response_model=schemas.Order)
def update_order(
    id: int, order: schemas.OrderUpdate, db: Session = Depends(get_db)
    ):
    db_order = crud.update_order(db=db, order=order, id=id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order


@app.delete("/orders/{id}", response_model=None)
def delete_order(
    id: int, db: Session = Depends(get_db)
    ):
    ret = crud.delete_order(db=db,  id=id)
    if ret is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return ret 


@app.get("/orders/", response_model=list[schemas.Order])
def read_orders(skip: int = 0, limit: int = 100, gte: int = 0 ,scode: str = '' ,db: Session = Depends(get_db)):

    db_orders = crud.get_orders(db, skip=skip, limit=limit, gte=gte, scode=scode)
    #if db_orders is None:
    #    raise HTTPException(status_code=404, detail="User not found")   
    return db_orders

@app.get("/orders/{id}", response_model=schemas.Order)
def read_orders_by_id(
    id: int, db: Session = Depends(get_db)
    ):
    db_order = crud.get_orders_by_id(db=db, order_id=id)
    if db_order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return db_order


#------- test --------
@app.get("/tests/", response_model=list[schemas.Test])
def read_tests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_tests(db, skip=skip, limit=limit)


#------- TPCL process -------
@app.get("/tpcledit",
    tags=['tpclmaker'],
    summary='Test page for sennd command',
    description='Test page for sennd command <br/>...............'
)
async def test_page():
    with open("test-tpcl.html",encoding="utf-8") as f:
        page = f.read()
    return Response(content=page,media_type="text/html")

@app.post("/tpclmaker/",tags=['tpclmaker'])
async def get_echo(body=Body(...)):
    ret = tpcl.tpcl_maker(body)
    if ret:
        with open('tpcl_send.log','r',encoding='utf-8') as f:
            response = f.read()
            return {"data":response}
    return {}
@app.post("/tpclmaker/status",tags=['tpclmaker'])
async def get_status(body=Body(...)):
        data =  tpcl.analize_status(body)
        return data
        #return {'status':'OK'}

#-------- convert process --------
@app.post("/convert/fromDB",tags=['convert DB'])
async def convert_from_masterDB(body=Body(...)):
        data =  convert_db()
        return data
        #return {'status':'OK'}

#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)