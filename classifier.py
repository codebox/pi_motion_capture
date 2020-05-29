from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.preprocessing import image
from tensorflow.keras.applications.mobilenet_v2 import preprocess_input, decode_predictions
import numpy as np
import time
import threading
import os.path
import os
import re

class Classifier:
    def __init__(self, config):
        self.config = config
        self.model = MobileNetV2(weights='imagenet')
        self.image_pattern = re.compile('{}[0-9]+\.jpg'.format(config['imgFileNamePrefix']))
        self.running = False

    def start(self):
        if not self.running:
            self.running = True
            self.worker_thread = threading.Thread(target=self._run)
            self.worker_thread.start()

    def _run(self):
        while self.running:
            for unclassified_file in [os.path.join(self.config['imageDir'], file) for file in os.listdir(self.config['imageDir']) if self.image_pattern.search(file)]:
                self._classify_image(unclassified_file)

            time.sleep(self.config['classificationPoll'])

    def _classify_image(self, image_path):
        print('classifying', image_path)
        img = image.load_img(image_path, target_size=(224, 224))
        x = image.img_to_array(img)
        x = np.expand_dims(x, axis=0)
        x = preprocess_input(x)
        predictions = self.model.predict(x)
        _, predicted_class, prob = decode_predictions(predictions, top=3)[0][0]
        if prob >= self.config['classificationThreshold']:
            self._label_image(image_path, predicted_class)
        else:
            self._label_image(image_path, 'unknown')

    def _label_image(self, image_file, label):
        image_filename = os.path.basename(image_file)
        name, ext = os.path.splitext(image_filename)
        new_name = '{}_{}{}'.format(name, label.replace(' ', '_'), ext)
        new_path = os.path.join(self.config['imageDir'], new_name)

        os.rename(image_file, new_path)

    def stop(self):
        self.running = False
