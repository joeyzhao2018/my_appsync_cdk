import os
import json
import boto3
from decimal import Decimal

# Import shared utilities if using layer
# from utils import get_table, format_response

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

# Helper class to convert Decimal to float for JSON serialization
class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def handler(event, context):
    try:
        # Query DynamoDB for all items
        response = table.scan()
        items = response['Items']

        # Handle pagination if necessary
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response['Items'])

        return  items

    except Exception as e:
        print(f"Error: {str(e)}")
