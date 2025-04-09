import os
import json
import boto3
from decimal import Decimal

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
        # Get item ID from event
        item_id = event['arguments']['id']

        # Query DynamoDB for specific item
        response = table.get_item(
            Key={
                'id': item_id
            }
        )

        # Check if item exists
        if 'Item' in response:
            return response['Item']
        else:
            return None
    except Exception as e:
        return {
            'error': str(e)
        }
