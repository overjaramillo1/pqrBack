from connection.db_connection import connect_to_database
from utils.general_utils import build_records
from utils.general_utils import response_api
from utils.token_manage import verify_token_access
import models.responses as STATUS_CODE
from datetime import datetime, timedelta
import pytz
import holidays

def main(event, context):
    if 'Authorization' not in event['headers']:
        return STATUS_CODE.UNAUTHORIZED
    data = event['body']
    token_data, profiles, username = verify_token_access(event['headers']['Authorization'])
    desired_time_zone = 'America/Bogota'
    current_time_with_zone = datetime.now(pytz.timezone(desired_time_zone))
    now_date = current_time_with_zone.strftime('%Y-%m-%d')
    conn = connect_to_database()
    if conn is None:
        return STATUS_CODE.INTERNAL_ERROR_SERVER
    cur = conn.cursor()
    try:
        cur.execute("select * from dbo.sp_get_request_report_all_by_filter(%s::date,%s::date,%s::int[],%s::character varying[],%s::int)",
                    (data['i_date'],
                     data['f_date'],
                     data['status_id'],
                     data['assigned_user'],
                     data['is_pqr']))
        column_names = [desc[0] for desc in cur.description]
        records = build_records(cur, column_names)
        for record in records:
            if record['status_name'] == 'Cerrada':
                record['request_days'] = get_request_days(record['filing_date'], record['answer_date'])
            else:
                record['request_days'] = get_request_days(record['filing_date'], now_date)
        cur.close()
        conn.close()
        return response_api(STATUS_CODE.OK['code'], STATUS_CODE.OK['message'], records)
    except Exception as e:
        cur.close()
        conn.close()
        print("error --> ", str(e))
        return STATUS_CODE.INTERNAL_ERROR_SERVER
def get_request_days(start_date_str, end_date_str):
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    co_holidays = holidays.Colombia()
    total_days = (end_date - start_date).days
    weekdays = 0
    # Iterate through each day between start_date and end_date
    for day in range(total_days):
        # Get the current date
        current_date = start_date + timedelta(days=day)
        
        # Check if the current date is not a weekend and not a holiday
        if current_date.weekday() < 5 and current_date not in co_holidays:
            weekdays += 1
    
    return weekdays