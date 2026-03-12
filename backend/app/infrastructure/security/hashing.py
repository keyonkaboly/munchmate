from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password) 

#returns true if user login password matches with hash password
def verify_password(password: str, hashed: str) -> bool:
    return pwd_context.verify(password, hashed) 

