import os
import cv2
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical
from mtcnn.mtcnn import MTCNN
from tensorflow.keras.applications.inception_resnet_v2 import InceptionResNetV2, preprocess_input
from tensorflow.keras.models import Model
from tensorflow.keras.layers import Layer, Flatten, Dense
from firebase_admin import storage
import tensorflow as tf

# Initialize MTCNN for face detection
detector = MTCNN()

def extract_face(image_data, required_size=(160, 160)):
    image = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = detector.detect_faces(image)
    if results:
        x1, y1, width, height = results[0]['box']
        x1, y1 = abs(x1), abs(y1)
        x2, y2 = x1 + width, y1 + height
        face = image[y1:y2, x1:x2]
        face = cv2.resize(face, required_size)
        return face
    return None

# class CustomScaleLayer(Layer):
#     def __init__(self, scale_factor=None, **kwargs):
#         self.scale_factor = scale_factor
#         super(CustomScaleLayer, self).__init__(**kwargs)
    
#     def build(self, input_shape):
#         super(CustomScaleLayer, self).build(input_shape)
    
#     def call(self, inputs, **kwargs):
#         if not isinstance(inputs, list):
#             inputs = [inputs]  # Ensure inputs is a list of tensors
        
#         scaled_inputs = [input_tensor * self.scale_factor for input_tensor in inputs]
#         if len(scaled_inputs) == 1:
#             return scaled_inputs[0]
#         else:
#             return scaled_inputs

#     def compute_output_shape(self, input_shape):
#         if isinstance(input_shape, list):
#             return [input_shape[0]]  # Return the same shape for each input tensor
#         else:
#             return input_shape

#     def get_config(self):
#         config = super(CustomScaleLayer, self).get_config()
#         config.update({'scale_factor': self.scale_factor})
#         return config

#     @classmethod
#     def from_config(cls, config):
#         scale_factor = config.pop('scale_factor', None)  # Remove scale_factor from config
#         return cls(scale_factor=scale_factor, **config) 
    
def initialize_model(num_classes):
    base_model = InceptionResNetV2(include_top=False, input_shape=(160, 160, 3), pooling='avg')
    x = Flatten()(base_model.output)
    output = Dense(num_classes, activation='softmax')(x)
    model = Model(inputs=base_model.input, outputs=output)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def create_label_map(bucket, prefixes):
    label_map = {}
    label_counter = 0
    for prefix in prefixes:
        blobs = list(bucket.list_blobs(prefix=prefix))
        for blob in blobs:
            label = blob.name.split('/')[1]
            if label and label not in label_map:
                label_map[label] = label_counter
                label_counter += 1
    return label_map

def retrain_model(model, model_path, bucket, prefixes, label_map):
    images = []
    labels = []

    for prefix in prefixes:
        blobs = list(bucket.list_blobs(prefix=prefix))
        if not blobs:
            print(f"No blobs found for prefix: {prefix}")
        for blob in blobs:
            label = blob.name.split('/')[1]
            if label in label_map:
                image_data = blob.download_as_bytes()
                face = extract_face(image_data)
                if face is not None:
                    face = face.astype('float32')
                    face = preprocess_input(face)
                    images.append(face)
                    labels.append(label_map[label])
                else:
                    print(f"No face detected in blob: {blob.name}")
            else:
                print(f"Label {label} not in label map")

    if not images or not labels:
        raise ValueError("No images or labels found for training")

    images = np.array(images)
    labels = np.array(labels)
    labels = to_categorical(labels, num_classes=len(label_map))

    if images.size == 0 or labels.size == 0:
        raise ValueError("Empty images or labels array")

    X_train, X_test, y_train, y_test = train_test_split(images, labels, test_size=0.2, random_state=42)

    history = model.fit(X_train, y_train, epochs=10, validation_data=(X_test, y_test))

    model.save(model_path)
    return model

@tf.function
def predict_face(face, model):
    return model(face, training=False)

def recognize_face(image_path, model, label_map):
    bucket = storage.bucket()
    blob = bucket.blob(image_path)
    image_data = blob.download_as_bytes()
    face = extract_face(image_data)
    if face is None:
        return None, None
    face = face.astype('float32')
    face = preprocess_input(face)
    face = np.expand_dims(face, axis=0)

    predictions = predict_face(face, model)
    predicted_class = np.argmax(predictions[0])
    confidence = predictions[0][predicted_class]

    label = {v: k for k, v in label_map.items()}[predicted_class]

    return label, confidence
