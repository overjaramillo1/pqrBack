from connection.db_connection import connect_to_database
from utils.general_utils import build_records
from utils.general_utils import response_api
import models.responses as STATUS_CODE

def main(event, context):
    print(event)
    print(context)
    entity = event['path']['entity']
    conn = connect_to_database()
    if conn is None:
        return STATUS_CODE.INTERNAL_ERROR_SERVER
    cur = conn.cursor()
    try:
        cur.execute(f"select * from dbo.sp_gen_get_all_{entity}()")
        column_names = [desc[0] for desc in cur.description]
        records = build_records(cur, column_names)
        cur.close()
        conn.close()
        return response_api(STATUS_CODE.OK['code'], STATUS_CODE.OK['message'], records)
    except Exception as e:
        cur.close()
        conn.close()
        print("error --> ", str(e))
        return STATUS_CODE.INTERNAL_ERROR_SERVER