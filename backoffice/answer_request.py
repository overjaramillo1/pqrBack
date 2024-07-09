from connection.db_connection import connect_to_database
from utils.general_utils import response_api
from utils.token_manage import verify_token_access
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
    if 'Authorization' not in event['headers']:
        return STATUS_CODE.UNAUTHORIZED
    data = event['body']
    token_data, profiles, username = verify_token_access(event['headers']['Authorization'])
    desired_time_zone = 'America/Bogota'
    current_time_with_zone = datetime.now(pytz.timezone(desired_time_zone))
    answer_time = current_time_with_zone.strftime('%Y-%m-%d %H:%M:%S+00:00')
    answer_date = current_time_with_zone.strftime('%Y-%m-%d')

    conn = connect_to_database()
    if conn is None:
        return STATUS_CODE.INTERNAL_ERROR_SERVER
    cur = conn.cursor()
    try:
        cur.execute("select * from dbo.sp_answer_request(%s::bigint,%s::int,%s::character varying,%s::character varying[],%s::character varying,%s::date,%s::date,%s::time with time zone)", 
                ( data["request_id"],
                  data["request_status"],  
                  data["request_answer"],
                  None,
                  username,
                  answer_date,
                  answer_date,
                  answer_time
                  ))
        conn.commit()
        notification = { 
        'username' : None,
        'user_email': None,
        'token_data' : None,
        'profiles' : None,
        'request_id' : data["request_id"],
        'assigned_user' : None,
        'action_id' : 2
        }
        print(notification)
        publish_event('send-email', 'notifications', notification)
        return response_api(STATUS_CODE.OK['code'], STATUS_CODE.OK['message'], 'updated')
    except Exception as e:
        conn.commit()
        conn.rollback()
        cur.close()
        conn.close()
        print("error --> ", str(e))
        return STATUS_CODE.INTERNAL_ERROR_SERVER