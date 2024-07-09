from connection.db_connection import connect_to_database
from utils.general_utils import build_records
from utils.general_utils import response_api
import models.responses as STATUS_CODE
from core.files_manager import upload_files

def handler(event, context):
    conn = connect_to_database()
    if conn is None:
        return STATUS_CODE.INTERNAL_ERROR_SERVER
    cur = conn.cursor()
    try:
        cur.execute("SELECT * from dbo.sp_decrease_requests_days()")
        column_names = [desc[0] for desc in cur.description]
        records = build_records(cur, column_names)
        conn.commit()
        cur.close()
        conn.close()
        return response_api(STATUS_CODE.OK['code'], STATUS_CODE.OK['message'], records)
    except Exception as e:
        conn.commit()
        conn.rollback()
        cur.close()
        conn.close()
        print("error --> ", str(e))
        return STATUS_CODE.INTERNAL_ERROR_SERVER