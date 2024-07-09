import uuid
import os
import boto3
from utils.general_utils import response_api
from connection.db_connection import connect_to_database
import models.responses as STATUS_CODE
import json
import re
from datetime import datetime
import pytz

BUCKET = os.environ["BUCKET_FILES"]
def cleanString(input_string):
    input_string = re.sub(r"[ _]", "-", input_string)
    return re.sub(r"[^a-zA-Z0-9\_\-\s]", "", input_string).lower()
def main(event, context):
    data = event['body']
    attachment_owner = event['path']['attachment_owner']
    if (attachment_owner != 'download'):
        request_id = data['request_id']
        sourceName = cleanString(str(data["source_name"].split(".")[0]))
        fileExtension = cleanString(str(data["source_name"].split(".")[-1]))
        desired_time_zone = 'America/Bogota'
        current_time_with_zone = datetime.now(pytz.timezone(desired_time_zone))
        now_time = current_time_with_zone.strftime('%H:%M:%S').replace(":","")
        now_date = current_time_with_zone.strftime('%Y-%m-%d')
        filename = f"{request_id}_{sourceName}.{fileExtension}"
        path = f"{now_date}/{filename}"
        location = 'https://'+BUCKET+'.s3.amazonaws.com/'+path+"@"+data['fileweight']
        try:
            s3 = boto3.client('s3')
        #upload_key = uuid.uuid4().hex
            key = f'{uuid.uuid4()}.png'
            presigned_url = s3.generate_presigned_url(
                ClientMethod='put_object',
                Params={
                    'Bucket': BUCKET,
                    'Key': path,
                    'ContentType': 'application/png',
                },
                ExpiresIn=3600,
                HttpMethod='PUT'
            )
            response = {
                'statusCode': 200,
                'headers': {
                'Access-Control-Allow-Origin': 'http://localhost:4200'
                },
                'body': json.dumps({
                    'presignedUrl': presigned_url,
                    'key': key
                })
            }
            if (attachment_owner == 'applicant'):
                upload_attach_location_applicant(location,request_id)
            elif (attachment_owner == 'assigned'):
                upload_attach_location_assigned(location,request_id)
            return response_api(STATUS_CODE.OK['code'], STATUS_CODE.OK['message'], presigned_url)
        except Exception as e:
            print("error --> ", str(e))
            return STATUS_CODE.INTERNAL_ERROR_SERVER
    else:
        parts = data['url'].split("/")
        path = "/".join(parts[3:])
        try:
            s3 = boto3.client('s3')
            presigned_url = s3.generate_presigned_url(
                ClientMethod='get_object',
                Params={
                    'Bucket': BUCKET,
                    'Key': path,
                },
                ExpiresIn=3600,
                HttpMethod='GET'
            )
            response = {
                'statusCode': 200,
                'headers': {
                'Access-Control-Allow-Origin': 'http://localhost:4200'
                },
                'body': json.dumps({
                    'presignedUrl': presigned_url
                })
            }
            return response_api(STATUS_CODE.OK['code'], STATUS_CODE.OK['message'], presigned_url)
        except Exception as e:
            print("error --> ", str(e))
            return STATUS_CODE.INTERNAL_ERROR_SERVER
def upload_attach_location_applicant(location,request_id):
    print(location)
    print(request_id)
    conn = connect_to_database()
    if conn is None:
        return STATUS_CODE.INTERNAL_ERROR_SERVER
    cur = conn.cursor()
    try:
        cur.execute("select * from dbo.sp_create_request_attachments(%s::bigint,%s::character varying[])", 
                ( request_id,
                  [location]
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
def upload_attach_location_assigned(location,request_id):
    conn = connect_to_database()
    if conn is None:
        return STATUS_CODE.INTERNAL_ERROR_SERVER
    cur = conn.cursor()
    try:
        cur.execute("select * from dbo.sp_create_answer_attachments(%s::bigint,%s::character varying[])", 
                ( request_id,
                  [location]
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