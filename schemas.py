from pydantic import BaseModel

class Cadastro(BaseModel):
    username:str
    email:str
    hashed_password:str
    
class PasswordResetRequest(BaseModel):
    email: str
    
class PasswordReset(BaseModel):
    password: str
    token: str
    