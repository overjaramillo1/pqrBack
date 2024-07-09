from connection.db_connection import connect_to_database
from utils.general_utils import build_records
from utils.general_utils import response_api
import models.responses as STATUS_CODE
from core.files_manager import download_file
from email_service.email_template import BODY_HTML_template
import boto3
from botocore.exceptions    import ClientError
from email.mime.multipart   import MIMEMultipart
from email.mime.text        import MIMEText
from email.mime.application import MIMEApplication
from string                 import Template
from models                 import responses as STATUS
import os
import base64
import time

CONFA_EMAIL_DOMAIN = os.environ['CONFA_EMAIL_DOMAIN']
AWS_REGION = os.environ['AWS_REGION']
SENDER = os.environ['SENDER']

def main(event, context):
    try:
        username = event['detail']['username']
        token_data = event['detail']['token_data']
        profiles = event['detail']['profiles']
        action_id = event['detail']['action_id']
        assigned_user = event['detail']['assigned_user']
        request_id = event['detail']['request_id']
    except Exception as exception:
        print('Bad input parameters --> ', exception)
    result = [username, token_data, profiles, action_id, assigned_user, request_id]
    configuration = get_notification_configuration(action_id)
    if action_id == 0:
        send_email_assigned_request(request_id,configuration)
    elif action_id == 1:
        send_email_created_request(request_id,configuration)
    elif action_id == 2:
        send_email_answered_request(request_id,configuration)
    return result

def send_email_assigned_request(request_id,configuration):
    request_details = get_request_details(request_id)
    subject = configuration['notification_name']
    notification_message = configuration['notification_message']
    # send_email(request_details['assigned_user'], request_details['assigned_user']+'@'+CONFA_EMAIL_DOMAIN, subject, notification_message, request_details, str(request_id), 'assigned')
    # if configuration['notification_receiver'] is not None and configuration['notification_receiver'] != ['']:
    #     for mail in configuration['notification_receiver']:
    #         send_email(mail.split("@")[0], mail, subject, notification_message, request_details, str(request_id), 'assigned')
def send_email_created_request(request_id,configuration):
    subject = configuration['notification_name']
    notification_message = configuration['notification_message']
    request_details = get_request_details(request_id)
    # send_email(request_details['applicant_name'], request_details['applicant_email'], subject, notification_message, request_details, str(request_id), 'created')
    # if configuration['notification_receiver'] is not None and configuration['notification_receiver'] != ['']:
    #     for mail in configuration['notification_receiver']:
    #         send_email(mail.split("@")[0], mail, subject, notification_message, request_details, str(request_id), 'created')
def send_email_answered_request(request_id,configuration):
    subject = configuration['notification_name']
    notification_message = configuration['notification_message']
    time.sleep(5)
    request_details = get_request_details(request_id)
    # try:
    #     send_email(request_details['applicant_name'], request_details['applicant_email'], subject, notification_message, request_details, str(request_id), 'answered')
    #     if configuration['notification_receiver'] is not None and configuration['notification_receiver'] != ['']:
    #         print('receivers')
    #         for mail in configuration['notification_receiver']:
    #             print(mail)
    #             send_email(mail.split("@")[0], mail, subject, notification_message, request_details, request_id, 'answered')
    #     else:
    #         print('no specific receivers')
    # except Exception as e:
    #     print("error --> ", str(e))
    #     return STATUS_CODE.INTERNAL_ERROR_SERVER
def get_notification_configuration(action_id):
    conn = connect_to_database()
    if conn is None:
        return STATUS_CODE.INTERNAL_ERROR_SERVER
    cur = conn.cursor()
    try:
        cur.execute("select * from dbo.sp_get_notification_by_action(%s::int)", (action_id,))
        column_names = [desc[0] for desc in cur.description]
        records = build_records(cur, column_names)
        cur.close()
        conn.close()
        return records[0]
    except Exception as e:
        conn.commit()
        conn.rollback()
        cur.close()
        conn.close()
        print("error --> ", str(e))
        return STATUS_CODE.INTERNAL_ERROR_SERVER

def get_request_details(request_id):
    conn = connect_to_database()
    if conn is None:
        return STATUS_CODE.INTERNAL_ERROR_SERVER
    cur = conn.cursor()
    try:
        cur.execute(f"select * from dbo.sp_get_request_by_id({request_id})")
        column_names = [desc[0] for desc in cur.description]
        records = build_records(cur, column_names)
        cur.close()
        conn.close()
        return records[0]
    except Exception as e:
        conn.commit()
        conn.rollback()
        cur.close()
        conn.close()
        print("error --> ", str(e))
        return STATUS_CODE.INTERNAL_ERROR_SERVER

def check_email_integrity(receiver_email):
    receiver_email_ = str(receiver_email)
    required_characters = ["@", "."]
    for required_char in required_characters:
        if required_char not in receiver_email_:
            return False
    return True

def send_email(first_name, receiver_email, subject, notification_message, request_details, request_id, event_action):
    print(request_details)
    print('email enviado a', receiver_email)
    try:
        if not check_email_integrity(receiver_email):
            return STATUS.BAD_REQUEST
    except Exception as e:
        print(str(e))
        return STATUS.BAD_REQUEST
    
    SUBJECT = subject
    BODY_TEXT = ""
    template = Template(BODY_HTML_template)
    if (event_action == 'assigned'):
        print('assigned')
        email_body = (notification_message.replace("$request_id",request_id).replace("{","<a href='https://master.d3avo25bjup8t5.amplifyapp.com/login'>").replace("}","</a>"))
        BODY_HTML = template.substitute(first_name=first_name, notification_message=email_body)
    elif (event_action == 'created'):
        print('created')
        email_body = (notification_message.replace("$filing_date",request_details['filing_date']).replace("$request_id",request_id).replace("[","<span class='dark'>").replace("]","</span>").replace("{","<a href='https://app.confa.co:8376/#/login'>").replace("}","</a>").replace("$line_jump","<br><br>"))
        BODY_HTML = template.substitute(first_name=first_name, notification_message=email_body)
    elif (event_action == 'answered'):
        print('answered')
        email_body = (notification_message.replace("$request_answer",request_details['request_answer']).replace("$request_id",str(request_id)).replace("$line_jump","<br><br>"))
        BODY_HTML = template.substitute(first_name=first_name, notification_message=email_body)
    CHARSET = "utf-8"
    
    client = boto3.client('ses',region_name=AWS_REGION)
    
    msg = MIMEMultipart('mixed')
    msg['Subject'] = SUBJECT 
    msg['From'] = SENDER 
    msg['To'] = receiver_email
    
    msg_body = MIMEMultipart('alternative')
    
    textpart = MIMEText(BODY_TEXT.encode(CHARSET), 'plain', CHARSET)
    htmlpart = MIMEText(BODY_HTML.encode(CHARSET), 'html', CHARSET)
    msg_body.attach(textpart)
    msg_body.attach(htmlpart)

    if (event_action == 'answered'):
        if request_details['assigned_attachments']:
            print('tiene assigned_attachments')
            attachments = request_details['assigned_attachments']
            for attach in attachments:
                path = attach.split('@')[0]
                weight = attach.split('@')[1]
                print(weight)
                parts = path.split('/')
                filename = '/'.join(parts[4:])
                desired_part = '/'.join(parts[3:])
                file_base64 = download_file(desired_part)
                file_bytes = base64.b64decode(file_base64)
                if len(file_bytes) <= 10485760:
                    att = MIMEApplication(file_bytes)
                    att.add_header('Content-Disposition','attachment',filename=filename)
                    msg.attach(att)
                else:
                    print('file is too long', len(file_bytes))
    msg.attach(msg_body)
    try:
        response = client.send_raw_email(
            Source=SENDER,
            Destinations=[
                receiver_email
            ],
            RawMessage={
                'Data':msg.as_string(),
            }
        )
    except ClientError as e:
        print(e.response['Error']['Message'])
        return STATUS.INTERNAL_ERROR_SERVER
    else:
        print("Email sent! Message ID:")
        print(response['MessageId'])
        return STATUS.OK