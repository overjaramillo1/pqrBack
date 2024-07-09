from connection.db_connection import connect_to_database
from utils.general_utils import response_api
import models.responses as STATUS_CODE
from datetime import datetime
import pytz
from core.files_manager import upload_files

def main(event, context):
    data = event['body']
    desired_time_zone = 'America/Bogota'
    current_time_with_zone = datetime.now(pytz.timezone(desired_time_zone))
    filing_time = current_time_with_zone.strftime('%Y-%m-%d %H:%M:%S+00:00')
    filing_date = current_time_with_zone.strftime('%Y-%m-%d')

    if data["applicant_attachments"] is not None:
        locations = []
        location = upload_files(filing_time, data["applicant_attachments"])
        locations.append(str(location)+"@"+data["applicant_attachments"]['fileweight'])
    conn = connect_to_database()
    if conn is None:
        return STATUS_CODE.INTERNAL_ERROR_SERVER
    cur = conn.cursor()
    try:
        cur.execute("select * from dbo.sp_create_request_attachments(%s::bigint,%s::character varying[])", 
                ( data["request_id"],
                  locations
                  ))
        conn.commit()
        return response_api(STATUS_CODE.OK['code'], STATUS_CODE.OK['message'], 'updated')
    except Exception as e:
        conn.commit()
        conn.rollback()
        cur.close()
        conn.close()
        print("error --> ", str(e))
        return STATUS_CODE.INTERNAL_ERROR_SERVER