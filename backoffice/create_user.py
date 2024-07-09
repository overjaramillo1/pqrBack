import models.responses as STATUS_CODE
from utils.general_utils import response_api
from utils.token_manage import verify_token_access
from datetime import datetime
import pytz
from connection.db_connection import connect_to_database
import uuid
import requests

VALIDATE_URL_ZION = "https://app.confa.co:8320/zionWS/rest/zion/metodo17"
ZION_GENERIC_PASSWORD = "3a76aacd6bc9e1d83c88f70c3216b257"
CONFA_DOMAIN =  "@confa"

def main(event, context):
    if 'Authorization' not in event['headers']:
        return STATUS_CODE.UNAUTHORIZED
    data = event['body']
    token_data, profiles, username = verify_token_access(event['headers']['Authorization'])
    user_validate_request = {
        "usuario" : data["user_name"],
        "contrasena" : ZION_GENERIC_PASSWORD,
        "sistema" : 54
        }
    response = requests.post(VALIDATE_URL_ZION, json=user_validate_request)
    print(response)
    if response.status_code != 200:
        return {"message": "POST request failed", "status_code": response.status_code}
    else:
        if (response.json() == STATUS_CODE.ZION_RESPONSE_NOT_FOUND):
            return response_api(STATUS_CODE.NO_CONTENT['code'], STATUS_CODE.NO_CONTENT['message'], response.json())
        else:
            created_user_profiles: str = response.json().get("perfiles")
            created_user_name: str = response.json().get("usuario")
            created_user_links: str = response.json().get("links")
            created_user_email = created_user_name + CONFA_DOMAIN
            print(created_user_email)
            print(response.json())
            #return response_api(STATUS_CODE.OK['code'], STATUS_CODE.OK['message'], profiles['nombre'])
            time_zone = 'America/Bogota'
            current_time_with_zone = datetime.now(pytz.timezone(time_zone))
            current_date = current_time_with_zone.strftime('%Y-%m-%d')
            conn = connect_to_database()
            if conn is None:
                return STATUS_CODE.INTERNAL_ERROR_SERVER
            cur = conn.cursor()
            try:
                cur.execute("select * from dbo.sp_createuser(%s::uuid,%s::character varying,%s::character varying,%s::int,%s::character varying,%s::date,%s::int,%s::int)", 
                        (uuid.uuid5(uuid.NAMESPACE_DNS, created_user_email),
                        created_user_name,
	                    created_user_email,
	                    2,
	                    username,
	                    current_date,
	                    1,
	                    1))
                conn.commit()
                return response_api(STATUS_CODE.OK['code'], STATUS_CODE.OK['message'], "created")
            except Exception as e:
                conn.commit()
                conn.rollback()
                cur.close()
                conn.close()
                print("error --> ", str(e))
                return STATUS_CODE.INTERNAL_ERROR_SERVER