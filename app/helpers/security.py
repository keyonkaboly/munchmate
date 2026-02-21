from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # Bcrypt allows max 72 bytes. Encoding within raw strings may exceed 72
    # So passwords will be truncated before being hashed.
    password = password[:72]
    return pwd_context.hash(password)

def verify_password(password: str, hashed: str) -> bool:
    password = password[:72]
    return pwd_context.verify(password, hashed)