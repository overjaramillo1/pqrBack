from connection.db_connection import connect_to_database
from utils.general_utils import build_records
from utils.general_utils import response_api
import models.responses as STATUS_CODE
from core.files_manager import download_file
from utils.token_manage import verify_token_access

def main(event, context):
    if 'Authorization' not in event['headers']:
        return STATUS_CODE.UNAUTHORIZED
    data = event['body']
    _, _, username = verify_token_access(event['headers']['Authorization'])
    print(username)
    content = download_file(data['download_url'])
    return response_api(STATUS_CODE.OK['code'], STATUS_CODE.OK['message'], content)