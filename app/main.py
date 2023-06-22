from fastapi import Depends, FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi import Body,Response
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import crud
import models
import schemas
from database import SessionLocal, engine
from fastapi.middleware.cors import CORSMiddleware
import tpcl_maker.tpcl_maker as tpcl
from convert.load_mysql_orm_view import convert_db
from convert.load_web import update_location

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

#app.mount("/", StaticFiles(directory="../front/quasar-app/dist/spa"), name="static")
# Quasarアプリケーションのビルド結果を提供するための設定
#app.mount("/spa", StaticFiles(directory="./spa"), name="static")
# Quasarアプリケーションのindex.htmlを提供する


@app.get("/home")
async def home():
#    return FileResponse("../front/quasar-app/dist/spa/index.html")
    return "hello"

@app.get("/slog")
async def send_log_view():
    return FileResponse("./tpcl_send.log")

@app.get("/rlog")
async def recv_log_view():
    return FileResponse("./tpcl_recv.log")

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
def read_orders(skip: int = 0, 
                limit: int = 100, 
                gte: int = 0 ,
                scode: str = '' ,
                place: str = '',
                db: Session = Depends(get_db)):

    db_orders = crud.get_orders(db, skip=skip, limit=limit, gte=gte, scode=scode,place=place)
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
    #if ret:
    #    with open('tpcl_send.log','r',encoding='utf-8') as f:
    #        response = f.read()
    #        return {"data":response}
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

@app.post("/convert/update_location",tags=['convert DB'])
async def update_location_from_web(body=Body(...)):
        data =  update_location()
        return data

#@app.get("/")
#async def index():
#    return FileResponse("./spa/index.html")
#    #return "hello"

#@app.get("/{full_path:path}")
#async def serve_static_file(full_path: str):
#    return FileResponse("./spa/" + full_path)


#if __name__ == "__main__":
#    uvicorn.run(app, host="0.0.0.0", port=8000)