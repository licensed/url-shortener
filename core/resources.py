from flask_restx import Namespace, Resource, fields
from flask import request, jsonify

from utils import generate_short_url

ns = Namespace('docs', description='ShortenURL')

shorten_url_model = ns.model('ShortenURL', {
    'url': fields.String(required=True, description='URL to be Shortened')
})


@ns.route('/shorten')
class ShortenURL(Resource):
    @ns.expect(shorten_url_model, validate=True)
    def post(self):
        """
        Shorten a URL.
        """
        data = request.json
        long_url = data.get('url')
        if long_url is None:
            return jsonify({'error': 'url is required.'}), 400
        short_url = generate_short_url()

        return jsonify({'short_url': short_url}), 201


@ns.route('/<string:short_url>')
class RedirectURL(Resource):
    def get(self, short_url):
        """
        Redirects to original URL.
        """
        return {'long_url': 'https://long.url'}


@ns.route('/<string:short_url>/update', methods=['PUT'])
class UpdateURL(Resource):
    def put(self, short_url):
        """
        Update URL.
        """
        return jsonify({'message': 'URL updated.'}), 200


@ns.route('/<string:short_url>/enable', methods=['PUT'])
class EnableURL(Resource):
    def put(self, short_url):
        """
        Enable URL.
        """

        return {'message': 'URL enabled.'}


@ns.route('/<string:short_url>/disable', methods=['PUT'])
class DisableURL(Resource):
    def put(self, short_url):
        """
        Disable URL.
        """

        return {'message': 'URL disabled.'}
