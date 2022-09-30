from urllib import response
from fastapi import Depends,FastAPI,HTTPException
from sqlalchemy.orm import Session

from . import crud,models,schemas
from .database import sessionLocal,engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = sessionLocal
    try:
        yield db
    finally:
        db.close_all()

@app.post("/users/",response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db,email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registerd")
    return crud.creeate_user(db=db,user=user)

    