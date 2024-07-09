from connection.db_connection import connect_to_database
from utils.general_utils import build_records
from utils.general_utils import response_api
import models.responses as STATUS_CODE

def main(event, context):
    form_id = event['path']['id']
    conn = connect_to_database()
    if conn is None:
        return STATUS_CODE.INTERNAL_ERROR_SERVER
    cur = conn.cursor()
    try:
        cur.execute(f"select * from dbo.sp_get_fields_form({form_id})")
        column_names = [desc[0] for desc in cur.description]
        records = build_records(cur, column_names)
        cur.close()
        conn.close()
        #_ = [get_catalog_by_id(record['catalog_source']) for record in records if record['catalog_source'] is not None]
        for record in records:
            if record['catalog_source'] is not None:
                record['catalog_source'] = get_catalog_by_id(record['catalog_source'])
        return response_api(STATUS_CODE.OK['code'], STATUS_CODE.OK['message'], records)
    except Exception as e:
        cur.close()
        conn.close()
        print("error --> ", str(e))
        return STATUS_CODE.INTERNAL_ERROR_SERVER
def get_catalog_by_id(catalog_id: int):
    conn = connect_to_database()
    if conn is None:
        return STATUS_CODE.INTERNAL_ERROR_SERVER
    cur = conn.cursor()
    try:
        cur.execute(f"select * from dbo.sp_get_catalog_items({catalog_id})")
        column_names = [desc[0] for desc in cur.description]
        records = build_records(cur, column_names)
        cur.close()
        conn.close()
        return records
    except Exception as e:
        cur.close()
        conn.close()
        print("error --> ", str(e))
        return STATUS_CODE.INTERNAL_ERROR_SERVER