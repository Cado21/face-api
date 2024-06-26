from flask import jsonify
from flask_restful import Resource
from firebase_admin import storage
from flasgger import swag_from

class StorageData(Resource):

    @swag_from({
        'tags': ['StorageData'],
        'responses': {
            '200': {
                'description': 'List of all data in storage',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'data': {
                            'type': 'array',
                            'items': {
                                'type': 'object',
                                'properties': {
                                    'name': {'type': 'string'},
                                    'size': {'type': 'integer'},
                                    'content_type': {'type': 'string'},
                                    'updated': {'type': 'string', 'format': 'date-time'},
                                    'created': {'type': 'string', 'format': 'date-time'}
                                }
                            }
                        }
                    }
                }
            },
            '500': {
                'description': 'Internal Server Error'
            }
        }
    })
    def get(self):
        try:
            bucket = storage.bucket()
            blobs = list(bucket.list_blobs())

            data = []
            for blob in blobs:
                data.append({
                    'name': blob.name,
                    'size': blob.size,
                    'content_type': blob.content_type,
                    'updated': blob.updated,
                    'created': blob.time_created
                })

            return jsonify({'data': data}), 200

        except Exception as e:
            return jsonify({'error': str(e)}), 500
