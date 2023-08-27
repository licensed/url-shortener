from flask import Flask, request, jsonify, redirect
from flask_restx import Api
from flask_caching import Cache
from util import generate_short_url
from core.db import table
from core.resources import ns

application = Flask(__name__)
application.config.from_object('config.BaseConfig')
api = Api(application, version='1.0', title='Shorten URLs API',
          description='Shorten URLs API', doc='/docs',)
api.add_namespace(ns)
cache = Cache(application)


@application.route('/shorten', methods=['POST'])
def shorten_url():
    long_url = request.get_json().get('url')

    if long_url is None:
        return jsonify({'error': 'url is required.'}), 400

    short_url = generate_short_url()

    table.put_item(Item={
        'short_url': short_url,
        'long_url': long_url,
        'active': 1
    })
    url = f"{request.url_root}{short_url}"
    return jsonify({'short_url': url}), 201


@application.route('/<short_url>', methods=['GET'])
@cache.cached(timeout=500)
def redirect_url(short_url):
    response = table.get_item(Key={'short_url': short_url})
    item = response.get('Item')
    if item and item.get('active') == 1:
        return redirect(item['long_url'])
    else:
        return jsonify({'error': 'URL not found'}), 404


@application.route('/<short_url>/enable', methods=['PUT'])
def enable_url(short_url):
    response = table.get_item(Key={'short_url': short_url})
    item = response.get('Item')
    if item:
        if item.get('active') == 1:
            return jsonify({'message': 'URL is already enabled.'}), 200
        else:
            table.update_item(
                Key={'short_url': short_url},
                UpdateExpression='SET active = :new_status',
                ExpressionAttributeValues={':new_status': 1}
            )
            return jsonify({'message': 'URL Enabled.'}), 200
    else:
        return jsonify({'error': 'URL not found'}), 404


@application.route('/<short_url>/disable', methods=['PUT'])
def disable_url(short_url):
    response = table.get_item(Key={'short_url': short_url})
    item = response.get('Item')
    if item:
        if item.get('active') == 0:
            return jsonify({'message': 'URL is already deactivated.'}), 200
        else:
            table.update_item(
                Key={'short_url': short_url},
                UpdateExpression='SET active = :new_status',
                ExpressionAttributeValues={':new_status': 0}
            )
            return jsonify({'message': 'URL Deactivated.'}), 200
    else:
        return jsonify({'error': 'URL not found'}), 404


@application.route('/<short_url>/update', methods=['PUT'])
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


# @application.route('/delete/<short_url>', methods=['DELETE'])
# def remove_url(short_url):
#     response = table.get_item(Key={'short_url': short_url})
#     item = response.get('Item')
#
#     if item:
#         table.delete_item(Key={'short_url': short_url})
#         return jsonify({'message': 'URL removed successfully.'}), 200
#     else:
#         return jsonify({'error': 'URL not found.'}), 404
