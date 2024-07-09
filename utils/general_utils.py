from datetime import date
import uuid

def clean_record(record_str):
    record = record_str[0].replace("(","").replace(")","").replace("\"", "")
    record = record.split(",")
    return record

def build_records(cursor, column_names):
    results = []
    for row in cursor.fetchall():
        result = {}
        for col_name, col_value in zip(column_names, row):
            if isinstance(col_value, date):
                result[col_name] = str(col_value)
            elif isinstance(col_value, uuid.UUID):
                result[col_name] = str(col_value)
            else:
                result[col_name] = col_value
        results.append(result)
    return results

def response_api(status, message, data):
    resp = {
        "code": status,
        "message": message,
        "data": data
    }
    return resp