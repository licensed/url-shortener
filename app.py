from flask import Flask, request, jsonify
import random
import string
import boto3

# from botocore.config import Config

app = Flask(__name__)

dynamodb = boto3.resource('dynamodb')
table_name = 'URLs'
table = dynamodb.Table(table_name)
URL_CHARS = 6


def generate_short_url():
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(URL_CHARS))


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
    print(short_url)
    response = table.get_item(Key={'short_url': short_url})
    item = response.get('Item')
    print(item)
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
        return jsonify({'message': 'URL removed.'}), 200
    else:
        return jsonify({'error': 'URL not found.'}), 404


if __name__ == '__main__':
    app.run(debug=True)
