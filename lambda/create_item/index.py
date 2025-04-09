import os
import json
import boto3
import uuid
import datetime

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    try:
        # Get item details from event
        name = event['arguments']['name']
        description = event.get('arguments', {}).get('description', '')

        # Generate unique ID and timestamps
        item_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now().isoformat()

        # Create new item
        item = {
            'id': item_id,
            'name': name,
            'description': description,
            'createdAt': timestamp,
            'updatedAt': timestamp
        }

        # Save to DynamoDB
        table.put_item(Item=item)

        return item
    except Exception as e:
        return {
            'error': str(e)
        }
