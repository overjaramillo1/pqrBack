from connection.db_connection import connect_to_database
from utils.general_utils import build_records
from utils.general_utils import response_api
from utils.token_manage import verify_token_access
import models.responses as STATUS_CODE

def main(event, context):
    if 'Authorization' not in event['headers']:
        return STATUS_CODE.UNAUTHORIZED
    token_data, profiles, username = verify_token_access(event['headers']['Authorization'])
    data = event['body']
    conn = connect_to_database()
    if conn is None:
        return STATUS_CODE.INTERNAL_ERROR_SERVER
    cur = conn.cursor()
    try:
        cur.execute("select * from dbo.sp_get_applicant_request_association(%s::int,%s::int)",
                    (data['page'],
                     data['page_size']))
        column_names = [desc[0] for desc in cur.description]
        records = build_records(cur, column_names)
        if records:
            total_count = records[0]['total_count']
        else:
            total_count = 0
        print(total_count)
        cur.close()
        conn.close()
        return response_api(STATUS_CODE.OK['code'], total_count, records)
    except Exception as e:
        cur.close()
        conn.close()
        print("error --> ", str(e))
        return STATUS_CODE.INTERNAL_ERROR_SERVER