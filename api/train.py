from flask import jsonify, request
from flask_restful import Resource
from firebase_admin import storage
from flasgger import swag_from

class Train(Resource):

    @swag_from({
        'tags': ['Train'],
        'parameters': [
            {
                'name': 'values',
                'type': 'array',
                'required': True,
                'description': 'Array of labels',
                'allowMultiple': True
            }
        ],
        'responses': {
            '200': {
                'description': 'Object of trained images',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            },
            '400': {
                'description': 'Missing values in request body'
            }
        }
    })
    def post(self):
        try:
            req_data = request.get_json()
            if not req_data or 'values' not in req_data:
                return jsonify({'message': 'Missing values in request body'}), 400
            
            values = req_data['values']
            result = {}

            bucket = storage.bucket()

            for label in values:
                folder_path = f"dataset/{label}/"
                blob_list = list(bucket.list_blobs(prefix=folder_path))

                if not blob_list:
                    continue

                image_names = [blob.name.split('/')[-1] for blob in blob_list if blob.name != folder_path]
                result[label] = image_names

            return jsonify(result), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
