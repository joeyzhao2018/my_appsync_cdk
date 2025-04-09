import os
import json
import boto3
import datetime

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TABLE_NAME'])

def handler(event, context):
    try:
        # Get item details from event
        item_id = event['arguments']['id']
        update_data = {}

        # Check which fields need updating
        if 'name' in event['arguments']:
            update_data['name'] = event['arguments']['name']

        if 'description' in event['arguments']:
            update_data['description'] = event['arguments']['description']

        # Add updated timestamp
        timestamp = datetime.datetime.now().isoformat()
        update_data['updatedAt'] = timestamp

        # Prepare update expression and attribute values
        update_expression = "SET "
        expression_attribute_values = {}

        for key, value in update_data.items():
            update_expression += f"{key} = :{key}, "
            expression_attribute_values[f":{key}"] = value

        # Remove trailing comma and space
        update_expression = update_expression.rstrip(", ")

        # Update item in DynamoDB
        response = table.update_item(
            Key={
                'id': item_id
            },
            UpdateExpression=update_expression,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW"
        )

        return response['Attributes']
    except Exception as e:
        return {
            'error': str(e)
        }
