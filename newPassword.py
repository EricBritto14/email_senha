from fastapi import APIRouter, Depends, HTTPException, status
from typing import Optional
from jose import jwt, JWTError
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from database import SessionLocal
import schemas, login, models
from schemas import *
from login import *
from models import *
# from .utils import create_access_token, verify_password
from jose import jwt
from smtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


router = APIRouter()

async def get_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

def get_user_by_email(db: Session, email: str):
    return db.query(Users).filter(Users.email == email).first()

def update_user_password(db: Session, username: str, hashed_password: str):
    user = db.query(Users).filter(Users.username == username).first()
    user.senha = hashed_password
    db.commit()

def generate_password_reset_token(email: str):
    expiration_time = datetime.utcnow() + timedelta(hours=1)
    payload = {"sub": email, "exp": expiration_time}
    token = jwt.encode(payload, "your-secret-key", algorithm="HS256")
    return token

def verify_password_reset_token(token: str):
    try:
        payload = jwt.decode(token, "your-secret-key", algorithms=["HS256"])
        return payload["sub"]
    except jwt.JWTError:
        return "erro"

def send_password_reset_email(email: str, token: str):
    sender_email = "eric.britto22@gmail.com"
    sender_password = "E40024041e"
    receiver_email = email
    subject = "Redefinição de Senha"
    body = f"""\
    Olá,

    Você solicitou uma redefinição de senha. Para redefinir sua senha, clique no link abaixo:

    http://localhost:8000/reset-password?token={token}

    Este link é válido por 1 hora.

    Se você não solicitou esta redefinição de senha, ignore este e-mail.

    Atenciosamente,
    Sua equipe de suporte
    """

    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject
    message.attach(MIMEText(body, "plain"))

    with SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        
        
@router.post("/forgot-password")
async def forgot_password(request: PasswordResetRequest, db: Session = Depends(get_session)):
    user = get_user_by_email(db, request.email)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail não encontrado")

    token = generate_password_reset_token(user.email)
    send_password_reset_email(user.email, token)
    return {"detail": "E-mail de redefinição de senha enviado com sucesso"}

@router.post("/reset-password")
async def reset_password(request: PasswordReset, db: Session = Depends(get_session)):
    email = verify_password_reset_token(request.token)
    if not email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Token inválido ou expirado")

    user = get_user_by_email(db, email)
    if not user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="E-mail não encontrado")

    hashed_password = get_password_hash(request.password)
    update_user_password(db, user.username, hashed_password)
    return {"detail": "Senha redefinida com sucesso"}