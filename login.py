from fastapi import APIRouter, HTTPException, Depends, Response, status, Cookie
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from passlib.context import CryptContext
from models import *
from database import engine, Base, SessionLocal

router = APIRouter()

def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        
class DBManager:
    @staticmethod
    def get_user(db:Session, username: str):
        return db.query(Users).filter(Users.username == username).first()
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str):
        user = DBManager.get_user(db, username)
        if user is None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuário inexistente")
        if not CryptContext(schemes=["bcrypt"]).verify(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha incorreta!")
        return user

def get_password_hash(password):
    return CryptContext(schemes=["bcrypt"]).hash(password)

@router.post("/login")
async def loginn(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    try:
        user = DBManager.authenticate_user(db, form_data.username, form_data.password)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuário ou senha incorreto")
        response.set_cookie(key="session", value=user.username)
        return {"message": "Login Bem Sucedido"}
    except Exception as e:
        print("Erro de vdd", str(e))
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    
def get_current_user(session: str = Cookie(None), db: Session = Depends(get_session)):
    user = DBManager.get_user(db, session)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Não logado")
    return user

@router.get("/protected")
def protected_route(user: Users = Depends(get_current_user)):
    return {"message": f"Olá, {user.username}"}