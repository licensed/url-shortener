from flask_restx import Namespace, Resource, fields
from flask import request

api = Namespace('', description='ShortenURL')

shorten_url_model = api.model('ShortenURL', {
    'url': fields.String(required=True, description='URL to be Shortened')
})


@api.route('/shorten')
class ShortenURL(Resource):
    @api.expect(shorten_url_model, validate=True)
    def post(self):
        """
        Shorten a URL.
        """
        data = request.json
        long_url = data.get('url')

        return {'short_url': 'https://shortened.url',
                'long_url': long_url,
                'active': 1}


@api.route('/<string:short_url>')
class RedirectURL(Resource):
    def get(self, short_url):
        """
        Redirects to original URL.
        """
        return {'long_url': 'https://long.url'}

    def put(self, short_url):
        """
        Update associated URL.
        """
        return {'message': 'URL updated'}

    def delete(self, short_url):
        """
        Delete URL.
        """
        return {'message': 'URL removed successfully.'}


namespace = api
