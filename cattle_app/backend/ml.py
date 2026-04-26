import os
from functools import lru_cache

MODEL_PATH = os.getenv(
    "CATTLE_MODEL_PATH",
    r"C:\Users\kumareshwary23\Desktop\cattle_marketplace_app\backend\models\cattle_model.h5",
)
LABELS = ["Gir", "Sahiwal", "Jersey", "Holstein", "Unknown"]


@lru_cache(maxsize=1)
def load_model():
    try:
        from tensorflow.keras.models import load_model as keras_load_model

        if os.path.exists(MODEL_PATH):
            return keras_load_model(MODEL_PATH)
    except Exception:
        return None
    return None


def predict_breed(image_path: str) -> str:
    model = load_model()
    if model is None:
        return "Unknown"

    try:
        import numpy as np
        from tensorflow.keras.preprocessing import image

        img = image.load_img(image_path, target_size=(224, 224))
        arr = image.img_to_array(img) / 255.0
        arr = np.expand_dims(arr, axis=0)
        prediction = model.predict(arr, verbose=0)[0]
        return LABELS[int(np.argmax(prediction))] if len(prediction) else "Unknown"
    except Exception:
        return "Unknown"
