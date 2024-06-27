from flask import Flask, request, jsonify
from flask_restful import Resource
from flasgger import swag_from
from firebase_admin import storage
from tensorflow.keras.models import load_model
from modules.face_recognition import recognize_face, create_label_map
from modules.custom_layers import CustomScaleLayer
import os
import tempfile
from tensorflow.keras.utils import get_custom_objects
from PIL import Image

# Register the custom layer
get_custom_objects().update({'CustomScaleLayer': CustomScaleLayer})

class RecognizeFace(Resource):

    @swag_from({
        'tags': ['Face Recognition'],
        'parameters': [
            {
                'name': 'image',
                'in': 'formData',
                'type': 'file',
                'required': True,
                'description': 'The image file to be recognized'
            },
            {
                'name': 'used_model',
                'in': 'formData',
                'type': 'string',
                'required': True,
                'description': 'The model name to be used for recognition'
            }
        ],
        'responses': {
            '200': {
                'description': 'Face recognized successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'label': {'type': 'string'},
                        'confidence': {'type': 'number'}
                    }
                }
            },
            '400': {
                'description': 'Bad request',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            },
            '500': {
                'description': 'Internal server error',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
    def post(self):
        try:
            # Check if the POST request has the file part
            if 'image' not in request.files:
                return jsonify({"error": "No image part in the request"}), 400
            
            file = request.files['image']
            
            if file.filename == '':
                return jsonify({"error": "No image selected for uploading"}), 400

            used_model = request.form.get('used_model')
            if not used_model:
                return jsonify({"error": "No model name provided"}), 400

            # Save the uploaded file to a temporary file
            temp_file = tempfile.NamedTemporaryFile(delete=False)
            file.save(temp_file.name)
            print('saved image file tmp')
            
            # Load the specified model
            model_path = f"models/{used_model}"
            bucket = storage.bucket()
            model_blob = bucket.blob(model_path)
            
            if not os.path.exists(model_path):
                if not model_blob.exists():
                    return {"error": f"Model {used_model} does not exist"}, 400
                model_blob.download_to_filename(model_path)
            print('downloaded model, loading model...')
            model = load_model(model_path, custom_objects={'CustomScaleLayer': CustomScaleLayer})

            # Create label map
            dataset_path = "dataset/"
            label_map = create_label_map(bucket, dataset_path)
            
            print('recognize_face')
            # Recognize the face using the loaded model
            label, confidence = recognize_face(temp_file.name, model, label_map)

            # Clean up the temporary file
            os.remove(temp_file.name)
            
            if label is None:
                return {"error": "No face detected"}, 400
            
            return {"label": label, "confidence": confidence}

        except Exception as e:
            return {"error": str(e)}, 500
