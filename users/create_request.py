from connection.db_connection import connect_to_database
from utils.general_utils import response_api
import models.responses as STATUS_CODE
from datetime import datetime
import pytz
import boto3
import json

def publish_event(source, detailtype, event):
    client = boto3.client('events')
    response = client.put_events(
        Entries = [
            {
                'Source': source,
                'DetailType': detailtype,
                'Detail': json.dumps(event)                
            },
        ]
    )
    return response['Entries'][0]['EventId']

def main(event, context):
    data = event['body']
    desired_time_zone = 'America/Bogota'
    current_time_with_zone = datetime.now(pytz.timezone(desired_time_zone))
    filing_time = current_time_with_zone.strftime('%Y-%m-%d %H:%M:%S+00:00')
    filing_date = current_time_with_zone.strftime('%Y-%m-%d')
    conn = connect_to_database()
    print("*************")
    print("data>>>or-peq")
    print(data)
    if conn is None:
        return STATUS_CODE.INTERNAL_ERROR_SERVER
    cur = conn.cursor()
    try:
        cur.execute("select * from dbo.sp_create_request(%s::date,%s::time with time zone,%s::int,%s::int,%s::int,%s::int,%s::character varying,%s::character varying,%s::character varying,%s::character varying,%s::character varying,%s::int,%s::character varying,%s::character varying,%s::boolean,%s::character varying[],%s::character varying[],%s::int)", 
                (filing_date, filing_time,
                  data["request_status"], 
                  data["applicant_type"], 
                  data["request_type"], 
                  data["doc_type"], 
                  data["doc_id"], 
                  data["applicant_name"], 
                  data["applicant_email"], 
                  data["applicant_cellphone"], 
                  data["request_description"],
                  data["request_days"],
                  data["assigned_user"],
                  data["request_answer"],
                  data["data_treatment"],
                  None,
                  data["assigned_attachments"],
                  data["form_id"]))
        conn.commit()
        result = cur.fetchone()
        print(result)
        notification = { 
        'username' : data["applicant_name"],
        'user_email': data["applicant_email"],
        'token_data' : None,
        'profiles' : None,
        'request_id' : result[0],
        'assigned_user' : None,
        'action_id' : 1
        }
        print(notification)
        publish_event('send-email', 'notifications', notification)
        return response_api(STATUS_CODE.OK['code'], STATUS_CODE.OK['message'], result[0])
    except Exception as e:
        conn.commit()
        conn.rollback()
        cur.close()
        conn.close()
        print("error --> ", str(e))
        return STATUS_CODE.INTERNAL_ERROR_SERVER