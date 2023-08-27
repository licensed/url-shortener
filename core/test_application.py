import unittest
from unittest.mock import patch, Mock
# from flask import Flask, jsonify
from application import application


class TestShortenURL(unittest.TestCase):
    @staticmethod
    def _get_mocked_dynamo_objects(expected_value):
        mock_batch_writer = Mock()
        mock_batch_writer.__enter__ = Mock(return_value=mock_batch_writer)
        mock_batch_writer.__exit__ = Mock(return_value=None)

        # Use side_effect or return_value according to your intention
        mock_batch_writer.put_item.side_effect = expected_value

        mock_table = Mock()
        mock_table.batch_writer.return_value = mock_batch_writer

        mock_db = Mock()
        mock_db.Table.return_value = mock_table

        return mock_db, mock_batch_writer
    def setUp(self):
        self.application = application.test_client()
    @patch('util.generate_short_url')
    @patch('boto3.resource')
    def test_shorten_url(self, mock_dynamo_db, mock_generate_short_url):
        mock_db, mock_batch_writer = self._get_mocked_dynamo_objects("db")
        mock_dynamo_db.return_value = mock_db
        mock_generate_short_url.return_value = 'abc123'

        response = self.application.post('/shorten', json={'url': 'http://www.someurl.com'})

        self.assertEqual(response.status_code, 201)
        # self.assertEqual(response.json, {'short_url': 'http://localhost/goVqtc'})

    def test_shorten_url_missing_url(self):
        response = self.application.post('/shorten', json={})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {'error': 'url is required.'})

    def test_redirect_url_valid(self):
        with patch('core.db.table.get_item') as mock_get_item:
            mock_get_item.return_value = {'Item': {'active': 1, 'long_url': 'http://www.example.com'}}
            response = self.application.get('/abc123')

            self.assertEqual(response.status_code, 302)
            self.assertEqual(response.headers['Location'], 'http://www.example.com')


    def test_redirect_url_inactive(self):
        with patch('core.db.table.get_item') as mock_get_item:
            mock_get_item.return_value = {'Item': {'active': 0}}
            response = self.application.get('/abc123')

            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, {'error': 'URL not found'})

    def test_redirect_url_not_found(self):
        with patch('core.db.table.get_item') as mock_get_item:
            mock_get_item.return_value = {}
            response = self.application.get('/abc123')

            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, {'error': 'URL not found'})

    def test_enable_url(self):
        with patch('core.db.table.get_item') as mock_get_item:
            mock_get_item.return_value = {'Item': {'active': 0}}
            with patch('core.db.table.update_item') as mock_update_item:
                response = self.application.put('/abc123/enable')

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json, {'message': 'URL Enabled.'})
                mock_update_item.assert_called_once_with(
                    Key={'short_url': 'abc123'},
                    UpdateExpression='SET active = :new_status',
                    ExpressionAttributeValues={':new_status': 1}
                )

    def test_enable_url_already_enabled(self):
        with patch('core.db.table.get_item') as mock_get_item:
            mock_get_item.return_value = {'Item': {'active': 1}}
            response = self.application.put('/abc123/enable')

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {'message': 'URL is already enabled.'})

    def test_enable_url_not_found(self):
        with patch('core.db.table.get_item') as mock_get_item:
            mock_get_item.return_value = {}
            response = self.application.put('/xyz789/enable')

            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, {'error': 'URL not found'})

    def test_disable_url(self):
        with patch('core.db.table.get_item') as mock_get_item:
            mock_get_item.return_value = {'Item': {'active': 1}}
            with patch('core.db.table.update_item') as mock_update_item:
                response = self.application.put('/abc123/disable')

                self.assertEqual(response.status_code, 200)
                self.assertEqual(response.json, {'message': 'URL Deactivated.'})
                mock_update_item.assert_called_once_with(
                    Key={'short_url': 'abc123'},
                    UpdateExpression='SET active = :new_status',
                    ExpressionAttributeValues={':new_status': 0}
                )

    def test_disable_url_already_disabled(self):
        with patch('core.db.table.get_item') as mock_get_item:
            mock_get_item.return_value = {'Item': {'active': 0}}
            response = self.application.put('/abc123/disable')

            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json, {'message': 'URL is already deactivated.'})

    def test_disable_url_not_found(self):
        with patch('core.db.table.get_item') as mock_get_item:
            mock_get_item.return_value = {}
            response = self.application.put('/xyz789/disable')

            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json, {'error': 'URL not found'})


if __name__ == '__main__':
    unittest.main()
