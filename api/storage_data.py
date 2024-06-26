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
                            'type': 'object',
                            'additionalProperties': {
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
            blobs = bucket.list_blobs(prefix='dataset/')
            data = {}
            for blob in blobs:
                print(f"Blob: {blob.name}, Size: {blob.size}")
                label = blob.name.split('/')[2]
                if label not in data:
                    data[label] = []
                    data[label].append({
                        'name': blob.name.split('/')[-1],
                        'size': blob.size,
                        'content_type': blob.content_type,
                        'updated': blob.updated.strftime('%Y-%m-%d %H:%M:%S'), 
                        'created': blob.time_created.strftime('%Y-%m-%d %H:%M:%S')
                    })
            
            return {'data': data}, 200

        except Exception as e:
            return {'error': str(e)}, 500
