from tensorflow.keras.models import load_model
from django.conf import settings
import numpy as np
import math
import cv2
import os
from .maxheight import max_height


def predict():
    path = os.path.join(settings.BASE_DIR, "make_miss_detector.h5")
    model = load_model(path)

    frames = []
    input_frame_path = settings.MEDIA_ROOT + '/frames/'
    img_size = 400

    img_list = os.listdir(input_frame_path)
    num_frames = len(img_list)

    for i in range(num_frames - 1):
        img_name = str(i) + '.png'
        img_path = os.path.join(input_frame_path, img_name)

        try:
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            frame_array = cv2.resize(img, (img_size, img_size))
            frames.append(frame_array)
        except:
            print(img_name + ' does not exist')

    frames = np.array(frames).reshape(-1, img_size, img_size, 1)
    frames = frames / 255

    raw_predictions = model.predict(frames)

    predictions = []

    for i in range(len(raw_predictions)):
        predictions.append(np.argmax(raw_predictions[i]))

    predictions = np.array(predictions)

    makes = 0
    misses = 0
    make_count = 0
    miss_count = 0
    make_height_frames = []
    miss_height_frames = []

    lower = upper = 0

    for prediction in predictions:
        if prediction == 1:
            miss_count += 1
        elif prediction == 2:
            make_count += 1
        else:
            miss_count = make_count = 0

        if miss_count > 5:
            misses += 1
            miss_count = make_count = -math.inf

            frame_name = max_height(lower, upper, prediction)
            miss_height_frames.append(frame_name)

            lower = upper

        if make_count > 5:
            makes += 1
            make_count = miss_count = -math.inf

            frame_name = max_height(lower, upper, prediction)
            make_height_frames.append(frame_name)

            lower = upper

        upper += 1

    total = makes + misses
    percentage = (makes / total) * 100

    array = [total, makes, misses, percentage]

    return array, make_height_frames, miss_height_frames
