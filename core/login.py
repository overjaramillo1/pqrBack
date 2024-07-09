import models.responses as STATUS_CODE
from utils.general_utils import response_api
import requests
import json
from datetime import datetime, timedelta
from jose import JWTError, jwt
import os

ACCESS_TOKEN_EXPIRE_MINUTES = os.environ['ACCESS_TOKEN_EXPIRE_MINUTES']
ALGORITHM = os.environ["ALGORITHM"]
SECRET_KEY = os.environ["SECRET_KEY"]
LOGIN_URL_ZION = os.environ["LOGIN_URL_ZION"]
VALIDATE_URL_ZION = os.environ["VALIDATE_URL_ZION"]
ZION_GENERIC_PASSWORD = os.environ["ZION_GENERIC_PASSWORD"]
def create_access_token_async(data):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"expire": expire.strftime("%Y-%m-%d %H:%M:%S")})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, ALGORITHM)
    payload = jwt.decode(encoded_jwt, SECRET_KEY, algorithms=ALGORITHM)
    print(payload)
    return encoded_jwt

def lambda_handler(event, context):
    payload = event['body']
    response = requests.post(LOGIN_URL_ZION, json=payload)
    print(response.text) #TEXT/HTML
    print(response.status_code, response.reason)

    if response.status_code == 200:
        if response.json() == STATUS_CODE.ZION_RESPONSE_UNAUTHORIZED:
            return response_api(STATUS_CODE.UNAUTHORIZED['code'], STATUS_CODE.ZION_RESPONSE_UNAUTHORIZED['estado'], STATUS_CODE.ZION_RESPONSE_UNAUTHORIZED['mensaje'])
        elif response.json() == STATUS_CODE.ZION_RESPONSE_NO_CONTENT:
            return response_api(STATUS_CODE.NO_CONTENT['code'], STATUS_CODE.ZION_RESPONSE_NO_CONTENT['estado'], STATUS_CODE.ZION_RESPONSE_NO_CONTENT['mensaje'])
        else:
            profiles = response.json().get("perfiles")
            name = response.json().get("usuario")
            links = response.json().get("links")

            # Asynchronously create access token
            user_token = create_access_token_async(response.json())
            print(user_token)

            return {
                'code': STATUS_CODE.OK['code'],
                'message': STATUS_CODE.OK['message'],
                'data': user_token
            }
    else:
        return {
            'statusCode': STATUS_CODE.INTERNAL_ERROR_SERVER['code'],
            'body': json.dumps({
                'error': 'Internal server error'
            })
        }