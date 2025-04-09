import json
import boto3
import datetime
import uuid

dynamodb = boto3.resource('dynamodb')

def get_table(table_name):
    return dynamodb.Table(table_name)

def format_response(status_code, body):
    return {
        'statusCode': status_code,
        'body': json.dumps(body),
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Credentials': True
        }
    }

def generate_id():
    return str(uuid.uuid4())

def get_timestamp():
    return datetime.datetime.now().isoformat()
