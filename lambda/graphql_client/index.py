import json
import os
import requests
import logging
from datetime import datetime

# Set up logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Get environment variables
GRAPHQL_API_URL = os.environ['GRAPHQL_API_URL']
GRAPHQL_API_KEY = os.environ['GRAPHQL_API_KEY']

# GraphQL queries and mutations
QUERY_GET_ITEMS = """
query GetItems {
  getItems {
    id
    name
    description
    createdAt
    updatedAt
  }
}
"""

MUTATION_CREATE_ITEM = """
mutation CreateItem($name: String!, $description: String) {
  createItem(name: $name, description: $description) {
    id
    name
    description
    createdAt
  }
}
"""

MUTATION_UPDATE_ITEM = """
mutation UpdateItem($id: ID!, $name: String, $description: String) {
  updateItem(id: $id, name: $name, description: $description) {
    id
    name
    description
    updatedAt
  }
}
"""

MUTATION_DELETE_ITEM = """
mutation DeleteItem($id: ID!) {
  deleteItem(id: $id) {
    id
    name
    description
  }
}
"""

QUERY_GET_ITEM_BY_ID = """
query GetItemById($id: ID!) {
  getItemById(id: $id) {
    id
    name
    description
    createdAt
    updatedAt
  }
}
"""


def make_graphql_request(query, variables=None):
    """Make a GraphQL request to the AppSync API"""
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': GRAPHQL_API_KEY
    }

    body = {
        'query': query,
        'variables': variables or {}
    }

    try:
        response = requests.post(
            GRAPHQL_API_URL,
            headers=headers,
            json=body
        )
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error making GraphQL request: {str(e)}")
        raise e

def create_demo_item():
    """Create a new demo item"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    variables = {
        'name': f'Demo Item {timestamp}',
        'description': f'This item was created by the client Lambda at {timestamp}'
    }

    result = make_graphql_request(MUTATION_CREATE_ITEM, variables)
    logger.info(f"Created new item: {json.dumps(result)}")
    return result['data']['createItem']['id'] if result.get('data') else None

def get_all_items():
    """Get all items"""
    result = make_graphql_request(QUERY_GET_ITEMS)
    items = result.get('data', {}).get('getItems', [])
    logger.info(f"Got {len(items)} items")
    return items

def update_random_item(items):
    """Update a random item from the list"""
    if not items:
        logger.info("No items to update")
        return

    import random
    item = random.choice(items)
    item_id = item['id']

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    variables = {
        'id': item_id,
        'description': f'This item was updated by the client Lambda at {timestamp}'
    }

    result = make_graphql_request(MUTATION_UPDATE_ITEM, variables)
    logger.info(f"Updated item {item_id}: {json.dumps(result)}")
    return item_id

def get_item_by_id(item_id):
    """Get a specific item by ID"""
    variables = {
        'id': item_id
    }

    result = make_graphql_request(QUERY_GET_ITEM_BY_ID, variables)
    logger.info(f"Got item by ID {item_id}: {json.dumps(result)}")
    return result.get('data', {}).get('getItemById')

def delete_random_item(items):
    """Delete a random item from the list"""
    if not items:
        logger.info("No items to delete")
        return

    import random
    item = random.choice(items)
    item_id = item['id']

    variables = {
        'id': item_id
    }

    result = make_graphql_request(MUTATION_DELETE_ITEM, variables)
    logger.info(f"Deleted item {item_id}: {json.dumps(result)}")

def handler(event, context):
    """Lambda handler function"""
    try:
        logger.info("Starting GraphQL client Lambda execution")

        # Demonstrate creating a new item
        item_id = create_demo_item()

        # Demonstrate getting all items
        items = get_all_items()

        # Demonstrate getting an item by ID
        if item_id:
            item = get_item_by_id(item_id)

        # Demonstrate updating an item
        if items:
            updated_id = update_random_item(items)

            # Get the updated item
            if updated_id:
                updated_item = get_item_by_id(updated_id)

        if items and len(items) > 3:  # Only delete if we have more than 3 items
            delete_random_item(items)

        # Demonstrate getting all items again after operations
        final_items = get_all_items()

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'GraphQL client Lambda executed successfully',
                'itemCount': len(final_items)
            })
        }
    except Exception as e:
        logger.error(f"Error in GraphQL client Lambda: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'message': f'Error in GraphQL client Lambda: {str(e)}'
            })
        }
