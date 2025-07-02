from passlib.context import CryptContext
from src.config.variables import SECRET_KEY
import bcrypt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hashPassword(password: str):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw((password + SECRET_KEY).encode('utf-8'), salt)
    return salt.decode('utf-8'), hashed.decode('utf-8')

def verifyPassword(plainPassword: str, hashedPassword: str) -> bool:

    try:
        return bcrypt.checkpw((plainPassword + SECRET_KEY).encode('utf-8'), hashedPassword.encode('utf-8'))
    except Exception as e:
        print(e)
        return False

def generateInviteLinkCode():
    import uuid
    
    # limit the length of the linkId to 10
    
    return str(uuid.uuid4().hex)[:10]


def CheckEmailFormat(email: str) -> bool:
    import re
    
    return bool(re.match(r"[^@]+@[^@]+\.[^@]+", email))