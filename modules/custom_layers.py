import tensorflow as tf

class CustomScaleLayer(tf.keras.layers.Layer):
    def __init__(self, scale=0.1, **kwargs):
        super(CustomScaleLayer, self).__init__(**kwargs)
        self.scale = scale

    def call(self, inputs):
        return inputs * self.scale

    def compute_output_shape(self, input_shape):
        return input_shape

    def compute_output_signature(self, input_signature):
        return tf.TensorSpec(shape=self.compute_output_shape(input_signature.shape), dtype=input_signature.dtype)

    def get_config(self):
        config = super(CustomScaleLayer, self).get_config()
        config.update({'scale': self.scale})
        return config
