import base64
import boto3
import models.extensions as EXTENSIONS
from utils.general_utils import response_api
import re
import string
import random
import os
import base64
import zlib

S3 = boto3.client("s3")
BUCKET = os.environ["BUCKET_FILES"]

def cleanString(input_string):
    input_string = re.sub(r"[ _]", "-", input_string)
    return re.sub(r"[^a-zA-Z0-9\_\-\s]", "", input_string).lower()
def generate_random_string(length):
    letters = string.ascii_letters
    random_string = "".join(random.choice(letters) for _ in range(length))
    return random_string

def upload_files(filing_time, attach):
            
    sourceName = cleanString(str(attach["source_name"].split(".")[0]))
    fileExtension = cleanString(str(attach["source_name"].split(".")[-1]))
    datenow = filing_time.split(" ")[0]
    timenow = filing_time.split(" ")[1].replace(":","").replace("+","")
    contentType = EXTENSIONS.mimetypes.get(fileExtension, "text/plain")
    bodyFile = base64.b64decode(attach["base64file"])
    filename = f"{timenow}_{sourceName}.{fileExtension}"
    path = f"{datenow}/{filename}"
    try:
        S3Result = S3.put_object(Bucket = BUCKET, Key = path, Body = bodyFile, ContentType = contentType)
    except Exception as e:
        return response_api(500, "Exception", str(e))
    
    responseMetadata = S3Result.get("ResponseMetadata", None)
    if responseMetadata is None:
        return response_api(500, "Error at uploading file. Bad response.", False)
    
    statusCode = responseMetadata.get("HTTPStatusCode", None)
    if statusCode == 200:
        location = f"https://{BUCKET}.s3.amazonaws.com/{path}"
        print(location)
        return location
    else:
        return response_api(500, f"Error at uploading file. Status: {statusCode}", None, False)
def upload_compressed_files(filing_time, attach):
            
    sourceName = cleanString(str(attach["source_name"].split(".")[0]))
    fileExtension = cleanString(str(attach["source_name"].split(".")[-1]))
    datenow = filing_time.split(" ")[0]
    timenow = filing_time.split(" ")[1].replace(":","").replace("+","")
    print(filing_time)
    print(datenow)
    print(timenow)

    contentType = EXTENSIONS.mimetypes.get(fileExtension, "text/plain")
    bodyFile = decompress_zlib_base64(attach["base64file"])
    #bodyFile = base64.b64decode(attach["base64file"])
    filename = f"{timenow}_{sourceName}.{fileExtension}"
    path = f"{datenow}/{filename}"
    try:
        S3Result = S3.put_object(Bucket = BUCKET, Key = path, Body = bodyFile, ContentType = contentType)
    except Exception as e:
        return response_api(500, "Exception", str(e))
    
    responseMetadata = S3Result.get("ResponseMetadata", None)
    if responseMetadata is None:
        return response_api(500, "Error at uploading file. Bad response.", False)
    
    statusCode = responseMetadata.get("HTTPStatusCode", None)
    if statusCode == 200:
        location = f"https://{BUCKET}.s3.amazonaws.com/{path}"
        print(location)
        return location
    else:
        return response_api(500, f"Error at uploading file. Status: {statusCode}", None, False)
def decompress_zlib_base64(encoded_data):
    decoded_data = base64.b64decode(encoded_data)
    decompressed_data = zlib.decompress(decoded_data)
    return decompressed_data
def upload_files_binary(filing_time, attach):
            
    sourceName = cleanString(str(attach["source_name"].split(".")[0]))
    fileExtension = cleanString(str(attach["source_name"].split(".")[-1]))
    datenow = filing_time.split(" ")[0]
    timenow = filing_time.split(" ")[1].replace(":","").replace("+","")

    contentType = EXTENSIONS.mimetypes.get(fileExtension, "text/plain")
    bodyFile = base64.b64decode(attach["base64file"])
    filename = f"{timenow}_{sourceName}.{fileExtension}"
    path = f"{datenow}/{filename}"
    try:
        S3Result = S3.put_object(Bucket = BUCKET, Key = path, Body = bodyFile, ContentType = contentType)
    except Exception as e:
        return response_api(500, "Exception", str(e))
    
    responseMetadata = S3Result.get("ResponseMetadata", None)
    if responseMetadata is None:
        return response_api(500, "Error at uploading file. Bad response.", False)
    
    statusCode = responseMetadata.get("HTTPStatusCode", None)
    if statusCode == 200:
        location = f"https://{BUCKET}.s3.amazonaws.com/{path}"
        print(location)
        return location
    else:
        return response_api(500, f"Error at uploading file. Status: {statusCode}", None, False)
def download_file(url_file):
    path = url_file
    print(path)
    try:
        S3Result = S3.get_object(Bucket=BUCKET, Key=path)
        content = S3Result['Body'].read()  # Read the content of the StreamingBody object
    except Exception as e:
        print('Error')
        return response_api(500, "Exception", str(e))
    
    responseMetadata = S3Result.get("ResponseMetadata", None)
    if responseMetadata is None:
        return response_api(500, "Error at uploading file. Bad response.", False)
    
    statusCode = responseMetadata.get("HTTPStatusCode", None)
    if statusCode == 200:
        # Encode the content in base64
        print('status llego')
        encoded_content = base64.b64encode(content).decode('utf-8')
        return encoded_content  # Return the base64 encoded content
    else:
        return response_api(500, f"Error at uploading file. Status: {statusCode}", None, False)
