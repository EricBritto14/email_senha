from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from login import *
import schemas, models, login, newPassword
from schemas import *
from models import *

Base.metadata.create_all(engine)

app = FastAPI()
app.include_router(login.router, tags=["Login"])
app.include_router(newPassword.router, tags=["Password Recovery"])

async def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        
@app.get("/get_users")
def getUsers(session: Session = Depends(get_session)):
    try:
        all = session.query(Users).all()
        return all
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

@app.post("/create_user")
def criando(user: schemas.Cadastro, session: Session = Depends(get_session)):
    try:
        item = Users(username = user.username, email = user.email, hashed_password = get_password_hash(user.hashed_password))
        session.add(item)
        session.commit()
        session.refresh(item)
        return item
    except Exception as e:
        session.rollback()
        print("Qq deu: ", str(e))
        return "Erro"
    