import numpy as np
import tensorflow.keras
from PIL import Image, ImageOps
import os

np.set_printoptions(suppress=True)
model_path = 'models/keras_model.h5'
model_path = os.path.normpath(model_path)
model = tensorflow.keras.models.load_model(model_path, compile=False)


def main(img, path):
    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    # path = 'video_frames/sd.mp4/' + img
    path = path + '/' + img
    image = Image.open(path)
    size = (224, 224)
    image = ImageOps.fit(image, size, Image.ANTIALIAS)
    image_array = np.asarray(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
    data[0] = normalized_image_array
    prediction = model.predict(data)
    # li.append(prediction)
    print(prediction)
    return prediction
