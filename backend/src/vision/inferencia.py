import os

import tensorflow as tf

MODEL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "..", "entrenamiento", "seadd_morfologia_savedmodel"
)
IMG_SIZE = 224
MORPH_CLASSES = ["macula", "papula", "escama"]  # training order — do not change

_preprocess = tf.keras.applications.efficientnet.preprocess_input  # backbone: EfficientNet-B0

_model = tf.keras.layers.TFSMLayer(MODEL_PATH, call_endpoint="serving_default")


def _cargar_imagen(image_path):
    img = tf.io.read_file(image_path)
    img = tf.image.decode_image(img, channels=3, expand_animations=False)
    img = tf.image.resize(img, [IMG_SIZE, IMG_SIZE])
    return _preprocess(tf.cast(img, tf.float32))[None, ...]


def predecir_morfologia(image_path):
    salida = _model(_cargar_imagen(image_path))
    if isinstance(salida, dict):
        salida = list(salida.values())[0]
    p = tf.convert_to_tensor(salida)[0].numpy()
    i = int(p.argmax())
    return {"morfologia": MORPH_CLASSES[i], "confianza": float(p[i])}
