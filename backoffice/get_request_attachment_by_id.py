from connection.db_connection import connect_to_database
from utils.general_utils import build_records
from utils.general_utils import response_api
from utils.token_manage import verify_token_access
import models.responses as STATUS_CODE
from datetime import datetime, timedelta
import pytz

def main(event, context):
    if 'Authorization' not in event['headers']:
        return STATUS_CODE.UNAUTHORIZED
    attachment_owner = event['path']['attachment_owner']
    data = event['body']
    request_id = data['request_id']
    desired_time_zone = 'America/Bogota'
    current_time_with_zone = datetime.now(pytz.timezone(desired_time_zone))
    now_date = current_time_with_zone.strftime('%Y-%m-%d')
    token_data, profiles, username = verify_token_access(event['headers']['Authorization'])
    conn = connect_to_database()
    if conn is None:
        return STATUS_CODE.INTERNAL_ERROR_SERVER
    cur = conn.cursor()
    try:
        cur.execute(f"select * from dbo.sp_get_request_attachments_by_id({request_id})")
        column_names = [desc[0] for desc in cur.description]
        records = build_records(cur, column_names)
        print(records)
        if (attachment_owner == 'applicant' and records[0]['applicant_attachments']):
            processed_attachments = preprocess_attachments(records[0]['applicant_attachments'], records[0]['filing_date'])
            result = paginate_attachments(processed_attachments, data['page'], data['page_size'])
        elif (attachment_owner == 'assigned' and records[0]['assigned_attachments']):
            processed_attachments = preprocess_attachments(records[0]['assigned_attachments'], records[0]['answer_date'])
            result = paginate_attachments(processed_attachments, data['page'], data['page_size'])
        else:
            result = []
            processed_attachments = []
        cur.close()
        conn.close()
        return response_api(STATUS_CODE.OK['code'], len(processed_attachments), result)
    except Exception as e:
        cur.close()
        conn.close()
        print("error --> ", str(e))
        return STATUS_CODE.INTERNAL_ERROR_SERVER
def preprocess_attachments(attachments,file_date):
    processed_attachments = []
    for attachment_url in attachments:
        parts = attachment_url.split('/')
        filename = parts[-1]
        filename_parts = filename.split('@')
        file_size = filename_parts[-1]
        file_name_without_size = '@'.join(filename_parts[:-1])
        last_dot_index = file_name_without_size.rfind('.')
        file_name = file_name_without_size[:last_dot_index]
        file_ext = file_name_without_size[last_dot_index + 1:]
        processed_attachment = {
            "url": attachment_url.split('@')[0],
            "file_name": file_name_without_size,
            "file_size": file_size,
            "file_ext": file_ext,
            "file_date": file_date
        }
        processed_attachments.append(processed_attachment)
    return processed_attachments
def paginate_attachments(processed_attachments, page, page_size):
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    return processed_attachments[start_index:end_index]