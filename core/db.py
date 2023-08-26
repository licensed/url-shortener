import boto3
import os
from dotenv import load_dotenv

load_dotenv()
ACCESS_KEY = os.environ.get('AWS_ACCESS_KEY_ID', '')
SECRET_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY', '')
table_name = 'URLs'
db = boto3.resource('dynamodb')
table = db.Table(table_name)


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

        table.wait_until_exists()
        return "Table created successfully!"

    except Exception as e:
        return "Error creating table: ", str(e)


def list_table(table_name):
    table = db.Table(table_name)
    response = table.scan()
    items = response['Items']
    for item in items:
        print(item)
