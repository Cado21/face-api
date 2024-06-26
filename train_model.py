from datetime import datetime
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import custom_object_scope
from firebase_admin import storage
from modules.face_recognition import initialize_model, create_label_map, retrain_model
from firebase_setup import initialize_firebase
import os

# Import the custom layer class here
from path.to.your.custom_scale_layer_module import CustomScaleLayer

# Global variables
labels_to_train = ["Ricardo", "Coda", "Dado"]
existing_model_name = "default_model_20240626_211244"  # Set to your existing model name if any, e.g., "existing_model_name"
dataset_path = "dataset/"  # Path to the dataset directory

def train_model(labels, model_name, dataset_path):
    if model_name is None:
        model_name = f'default_model_{datetime.now().strftime("%Y%m%d_%H%M%S")}'

    model_path = f"models/{model_name}.h5"
    bucket = storage.bucket()

    # Prefixes based on labels
    prefixes = [f'{dataset_path}{label}/' for label in labels]

    # Check if the model exists
    model_blob = bucket.blob(model_path)
    if model_blob.exists():
        # Download and load the existing model
        local_model_path = f"{model_name}.h5"
        model_blob.download_to_filename(local_model_path)

        # Register the custom layer
        with custom_object_scope({'CustomScaleLayer': CustomScaleLayer}):
            model = load_model(local_model_path)
    else:
        # Initialize a new model if it doesn't exist
        label_map = create_label_map(bucket, dataset_path)
        model = initialize_model(len(label_map))

    # Retrain the model with new images from Firebase Storage
    label_map = create_label_map(bucket, dataset_path)
    model = retrain_model(model, model_path, bucket, prefixes, label_map)

    # Upload the updated model to Firebase Storage
    model.save(model_path)
    model_blob.upload_from_filename(model_path)

    print(f'Model {model_path} retrained and uploaded successfully.')

    # Remove local model file after uploading
    if os.path.exists(model_path):
        os.remove(model_path)
        print(f'Local file {model_path} removed.')

if __name__ == "__main__":
    initialize_firebase()
    train_model(labels_to_train, existing_model_name, dataset_path)
