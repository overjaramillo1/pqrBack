from connection.db_connection import connect_to_database
from utils.general_utils import response_api
from utils.token_manage import verify_token_access
import models.responses as STATUS_CODE
from datetime import datetime
import pytz

def main(event, context):
    if 'Authorization' not in event['headers']:
        return STATUS_CODE.UNAUTHORIZED
    print(event['headers']['Authorization'])
    token_data, profiles, username = verify_token_access(event['headers']['Authorization'])
    print(token_data)
    print(profiles)
    print(username)
    data = event['body']
    desired_time_zone = 'America/Bogota'
    current_time_with_zone = datetime.now(pytz.timezone(desired_time_zone))
    filing_time = current_time_with_zone.strftime('%Y-%m-%d %H:%M:%S+00:00')
    filing_date = current_time_with_zone.strftime('%Y-%m-%d')

    conn = connect_to_database()
    if conn is None:
        return STATUS_CODE.INTERNAL_ERROR_SERVER
    cur = conn.cursor()
    try:
        cur.execute("select * from dbo.sp_characterize_request(%s::bigint,%s::bigint,%s::bigint,%s::int,%s::int,%s::int,%s::int,%s::int,%s::character varying,%s::date)", 
                ( data["request_id"],
                  data["applicant_type_id"],
                  data["request_type_id"],
                  data["is_pqr"], 
                  data["quality_dimension_id"], 
                  data["modality_id"], 
                  data["category_id"], 
                  data["month"], 
                  username,
                  filing_date))
        conn.commit()
        return response_api(STATUS_CODE.OK['code'], STATUS_CODE.OK['message'], 'created')
    except Exception as e:
        conn.commit()
        conn.rollback()
        cur.close()
        conn.close()
        print("error --> ", str(e))
        return STATUS_CODE.INTERNAL_ERROR_SERVER