from connection.db_connection import connect_to_database
from utils.general_utils import build_records
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
    print(token_data)
    print(profiles)
    print(username)
    notification = { 
        'username' : username,
        'token_data' : token_data,
        'profiles' : profiles,
        'request_id' : data['request_id'],
        'assigned_user' : data['assigned_user'],
        'action_id' : 0
        }
    print(notification)
    publish_event('send-email', 'notifications', notification)
    time_zone = 'America/Bogota'
    current_time_with_zone = datetime.now(pytz.timezone(time_zone))
    current_date = current_time_with_zone.strftime('%Y-%m-%d')
    conn = connect_to_database()
    if conn is None:
        return STATUS_CODE.INTERNAL_ERROR_SERVER
    cur = conn.cursor()
    try:
        cur.execute("select * from dbo.sp_assign_user_to_request(%s::bigint,%s::character varying,%s::int,%s::character varying,%s::date)", 
                (data['request_id'],
                 data['assigned_user'],
                 data['request_status'],
                 username,
	             current_date
                 ))
        conn.commit()
        return response_api(STATUS_CODE.OK['code'], STATUS_CODE.OK['message'], "created")
    except Exception as e:
        conn.commit()
        conn.rollback()
        cur.close()
        conn.close()
        print("error --> ", str(e))
        return STATUS_CODE.INTERNAL_ERROR_SERVER