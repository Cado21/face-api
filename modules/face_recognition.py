from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Conv2D, MaxPooling2D
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.optimizers import Adam
from firebase_admin import storage
import tensorflow as tf
import os
from PIL import Image


def initialize_model(num_classes):
    model = Sequential([
        Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
        MaxPooling2D((2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        CustomScaleLayer(),
        Dense(num_classes, activation='softmax')
    ])
    model.compile(optimizer=Adam(), loss='categorical_crossentropy', metrics=['accuracy'])
    return model

def create_label_map(bucket, dataset_path):
    blobs = bucket.list_blobs(prefix=dataset_path)
    labels = {blob.name.split('/')[1] for blob in blobs}
    label_map = {label: idx for idx, label in enumerate(sorted(labels))}
    return label_map

def retrain_model(model, model_path, bucket, prefixes, label_map):
    datagen = ImageDataGenerator(rescale=0.1)

    train_generator = datagen.flow_from_directory(
        'dataset',
        target_size=(224, 224),
        batch_size=32,
        class_mode='categorical'
    )

    model.fit(
        train_generator,
        steps_per_epoch=train_generator.samples // train_generator.batch_size,
        epochs=10
    )

    model.save(model_path)
    model_blob = bucket.blob(model_path)
    model_blob.upload_from_filename(model_path)
    
    return model

def recognize_face(image_path, model, label_map):
    image = tf.keras.preprocessing.image.load_img(image_path, target_size=(160, 160))
    image = tf.keras.preprocessing.image.img_to_array(image)
    image = tf.expand_dims(image, axis=0)
    image = image / 255.0

    predictions = model.predict(image)
    predicted_label_idx = tf.argmax(predictions, axis=1).numpy()[0]
    confidence = predictions[0][predicted_label_idx]

    label_map_reversed = {v: k for k, v in label_map.items()}
    predicted_label = label_map_reversed[predicted_label_idx]

    return predicted_label, confidence
