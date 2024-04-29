from sqlalchemy import String, Integer, Float, Column
from database import Base

class Users(Base):
    __tablename__ = 'users'
    idUsuario: int = Column(Integer, primary_key=True)
    username: String = Column(String(200), nullable=False, unique=True)
    email: String = Column(String(200), nullable=False, unique=True)
    hashed_password: String = Column(String(200), nullable=False)
    