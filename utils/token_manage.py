import os
import models.responses as STATUS_CODE
from datetime import datetime, timedelta
from jose import JWTError, jwt
from utils.general_utils import response_api

SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = os.environ['ALGORITHM']
ACCESS_TOKEN_EXPIRE_MINUTES = os.environ['ACCESS_TOKEN_EXPIRE_MINUTES']

async def create_access_token(data):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"expire": expire.strftime("%Y-%m-%d %H:%M:%S")})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    payload = jwt.decode(encoded_jwt, SECRET_KEY, algorithms=ALGORITHM)
    print(payload)
    return encoded_jwt

def verify_token_access(token):
    try:
        validate_jwt(token)
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        username: str = payload.get("usuario")
        profiles: str = payload.get("perfiles")
        links: str = payload.get("links")
        profiles = [item["nombre"] for item in profiles]
        #print(profiles)
    except JWTError as e:
        print("error --> ", str(e))
    return (payload,profiles, username)

def validate_jwt(token):
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM, options={"verify_signature": False})
        expiration_time = decoded_token.get("expire")
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if expiration_time > current_time:
            print("JWT is valid and not expired")
        else:
            print("JWT has expired")
            raise Exception(status_code=STATUS_CODE.UNAUTHORIZED, detail="JWT has expired")
    except JWTError as e:
        raise Exception(status_code=STATUS_CODE.UNAUTHORIZED, detail="Invalid JWT token")
def refresh_token(event, context):
    data = event['body']
    token = data['token']
    try:
        decoded_token = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM, options={"verify_signature": False})
        expiration_time = decoded_token.get("expire")
        current_time = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        if expiration_time > current_time:
            print("JWT is valid and not expired")  
            expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
            new_token = decoded_token.update({"expire": expire.strftime("%Y-%m-%d %H:%M:%S")})
            encoded_jwt = jwt.encode(new_token, SECRET_KEY, ALGORITHM)
            return response_api(STATUS_CODE.OK['code'], STATUS_CODE.OK['message'], encoded_jwt)
        else:
            print("JWT has expired")
            raise Exception(status_code=STATUS_CODE.UNAUTHORIZED, detail="JWT has expired")
    except JWTError as e:
        raise Exception(status_code=STATUS_CODE.UNAUTHORIZED, detail="Invalid JWT token")