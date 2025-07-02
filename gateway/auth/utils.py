from dotenv import load_dotenv
import os
from jose import JWTError
import jwt

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")

def ValidateToken(token):
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY is not set in the environment variables.")
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        print(payload)
        return payload
    except JWTError as e:
        print(e)

        if "expired" in str(e).lower():
            print("Token has expired.")
        elif "signature" in str(e).lower():
            print("Invalid signature.")
        else:
            print(f"JWT Error: {e}")
        return None