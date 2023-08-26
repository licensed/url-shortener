from flask import Flask, request, jsonify
from flask_restx import Api

from utils import generate_short_url
from controller import namespace
import boto3

app = Flask(__name__)
api = Api(app, version='1.0', title='Shorten URLs API',
          description='Shorten URLs API')

api.add_namespace(namespace)

dynamodb = boto3.resource('dynamodb')
table_name = 'URLs'
table = dynamodb.Table(table_name)
URL_CHARS = 6


@app.route('/shorten', methods=['POST'])
def shorten_url():
    data = request.get_json()
    long_url = data.get('url')

    if long_url is None:
        return jsonify({'error': 'url is required.'}), 400

    short_url = generate_short_url()

    table.put_item(Item={
        'short_url': short_url,
        'long_url': long_url,
        'active': 1
    })

    return jsonify({'short_url': short_url}), 201


@app.route('/<short_url>', methods=['GET'])
def redirect_url(short_url):
    response = table.get_item(Key={'short_url': short_url})
    item = response.get('Item')
    if item:
        return jsonify({'long_url': item['long_url']})
    else:
        return jsonify({'error': 'URL not found'}), 404


@app.route('/edit/<short_url>', methods=['PUT'])
def edit_url(short_url):
    data = request.get_json()
    new_long_url = data.get('new_url')

    response = table.get_item(Key={'short_url': short_url})
    item = response.get('Item')

    if not item:
        return jsonify({'error': 'URL not found.'}), 404

    table.update_item(
        Key={'short_url': short_url},
        UpdateExpression='SET long_url = :new_url',
        ExpressionAttributeValues={':new_url': new_long_url}
    )

    return jsonify({'message': 'URL updated.'}), 200


@app.route('/delete/<short_url>', methods=['DELETE'])
def remove_url(short_url):
    response = table.get_item(Key={'short_url': short_url})
    item = response.get('Item')

    if item:
        table.delete_item(Key={'short_url': short_url})
        return jsonify({'message': 'URL removed successfully.'}), 200
    else:
        return jsonify({'error': 'URL not found.'}), 404


if __name__ == '__main__':
    app.run(debug=True)
