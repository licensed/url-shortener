import boto3
import os
from string import ascii_letters, digits
from random import choice

URL_CHARS = os.environ.get('URL_CHARS', 6)
dynamodb = boto3.resource('dynamodb')
table_name = 'URLs'


def generate_short_url():
    characters = ascii_letters + digits
    return ''.join(choice(characters) for _ in range(URL_CHARS))


def create_table(dynamodb, table_name):
    try:
        table = dynamodb.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'short_url',
                    'KeyType': 'HASH'  # Partition key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'short_url',
                    'AttributeType': 'S'
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )

        print("Table created successfully!")

    except Exception as e:
        print("Error creating table:", str(e))


def list_table(table_name):
    table = dynamodb.Table(table_name)
    response = table.scan()
    items = response['Items']
    for item in items:
        print(item)
