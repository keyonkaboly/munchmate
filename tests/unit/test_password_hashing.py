from app.infrastructure.security.hashing import hash_password, verify_password

def test_hash_password():
    password = "mysecretpassword"
    hashed = hash_password(password)
    
    assert hashed != password
    
def test_verify_password_success():
    password = "meowmeow"
    hashed = hash_password(password)
    
    assert verify_password(password, hashed) is True
    

def test_verify_password_faillure():
    password = "meowmeow"
    hashed = hash_password(password)
    
    assert verify_password("ruffruff", hashed) is False
    
