from flask import jsonify, request
from flask_restful import Resource
from flasgger import swag_from
from werkzeug.utils import secure_filename
from firebase_admin import storage

class AddDataset(Resource):

    @swag_from({
        'tags': ['Dataset'],
        'parameters': [
            {
                'name': 'label',
                'in': 'formData',
                'type': 'string',
                'required': True,
                'description': 'The label for the dataset'
            },
            {
                'name': 'images',
                'in': 'formData',
                'type': 'file',
                'required': True,
                'description': 'The images to be uploaded',
                'allowMultiple': True
            }
        ],
        'responses': {
            '200': {
                'description': 'Images successfully uploaded',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            }
        }
    })
    def post(self):
        try:
            label = request.form.get('label')

            if 'images' not in request.files:
                return jsonify({'message': 'No images part in the request'}), 400
            
            images = request.files.getlist('images')

            if not images:
                return jsonify({'message': 'No images provided'}), 400

            # Folder path in Firebase Storage
            folder_path = f"dataset/{label}/"

            for image in images:
                filename = secure_filename(image.filename)
                blob = storage.bucket().blob(f"{folder_path}{filename}")
                blob.upload_from_string(image.read(), content_type=image.content_type)

            return {'label': label}, 200
        except Exception as e:
            print(e)
            return {'error': 'Something went wrong!'}, 500
