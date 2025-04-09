import os
import json
import boto3

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    try:
        # Get item ID from event
        item_id = event['arguments']['id']

        # Get the item first to return it
        get_response = table.get_item(
            Key={
                'id': item_id
            }
        )

        if 'Item' not in get_response:
            return None

        # Delete the item
        table.delete_item(
            Key={
                'id': item_id
            }
        )

        # Return the deleted item
        return get_response['Item']
    except Exception as e:
        return {
            'error': str(e)
        }
