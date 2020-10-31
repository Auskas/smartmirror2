#!/usr/bin/python3
# gestures.py
#
# The module uses a trained CNN to recognize static hand gestures in the top right area of the video capture.
# The area, also known as ROI, is a square which side length is given by the self.ROI_SIZE variable.
# The ROI is preprocessed before it is conveyed to the CNN:
#   - the background is substracted from the ROI;
# The CNN gets the processed ROI and determines the static gesture. The result can be:
#   - one of the following gestures are detected: five fingers open palm, four fingers, the peace sign,
#                                                 sign of the horns, thumb up, inverted L, and the pointing finger;
#   - None. That means that the CNN is absolutely sure there is no known static hand gestures in the ROI;
#   - Unknown. The CNN detects a static hand gesture in the ROI, but the level of certainty is below the threshold.
#     The threshold can be changed in the 'predictor' method.
#     The local variable 'prediction' is compaired against the threshold.

from tensorflow.keras.models import load_model
import numpy as np
import cv2
import os, sys, copy
import logging
import time

class GesturesRecognizer:

    def __init__(self, *args):
        self.logger = logging.getLogger('SM.gestures')

        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)

        bg_thresh = 500
        self.background_substractor = cv2.createBackgroundSubtractorMOG2(
            detectShadows=False,
            varThreshold=bg_thresh
            )
        self.kernel = np.ones((4,4),np.uint8)
        self.dilation_kernel = np.ones((3,3),np.uint8)

        self.LABELS = [
            '5',
            '4',
            'inverted_l',
            'peace',
            'pointing_finger',
            None,
            'sign_of_the_horns',
            'thumb_up'
        ]

        self.ROI_SIZE = 250
        self.IMG_SIZE = 32 # the CNN is trained on the given images' sizes
        self.FPS = 30 # the number of frames analyzed per second.

        if __name__ == '__main__':
            self.camera = cv2.VideoCapture(0)
            self.queue = False
        else:
            self.camera = args[0]
            self.queue = args[1]

        if self.camera.isOpened()== False:
            self.logger.critical("Error opening video stream or file")
        _, self.frame = self.camera.read()

        #self.camera.set(10, 1) # Sets the brightness of the camera.
        #self.camera.set(11, 50) # Sets the contrast of the camera.
        #self.camera.set(cv2.CAP_PROP_EXPOSURE, 40)

        self.MODEL_IMG_SIZE = 32

        self.begin_X, self.begin_Y = int(self.frame.shape[1] - self.ROI_SIZE), 0
        self.end_X, self.end_Y = self.frame.shape[1], self.ROI_SIZE

        self.predicted_gesture = None # Detected static hand gesture.

        self.logger.info('Gestures recognizer has been initialiazed!')

    def predictor(self, frame, roi):
        try:
            roi_copy = roi

            roi_copy = cv2.resize(roi_copy, (self.MODEL_IMG_SIZE, self.MODEL_IMG_SIZE))
            roi_copy = roi_copy / 255.0
            roi_copy = roi_copy.reshape(-1, self.MODEL_IMG_SIZE, self.MODEL_IMG_SIZE, 1)

            prediction = self.model.predict(roi_copy)
            i = prediction.argmax(axis=-1)[0]
            if prediction[0][i] * 100 > 70:
                self.predicted_gesture = self.LABELS[i]
            else:
                self.predicted_gesture = None

            if __name__ == '__main__':
                if prediction[0][i] * 100 > 70:
                    text = f'{str(self.LABELS[i])} {prediction[0][i]*100:.2f}%'
                    color = (0, 0, 255)
                else:
                    text = 'Unknown'
                    color = (0, 0, 255)
                cv2.putText(frame, text, (10,30), cv2.FONT_HERSHEY_SIMPLEX, 1, color , 4)

        except Exception as exc:
            self.predicted_gesture = None
            self.logger.error(f'Cannot predict the gesture: {exc}')



    def tracker(self):

        # When using multiprocessing with the current module,
        # the model must be loaded inside a child process.
        try:
            self.model = load_model(f'data{os.sep}gestures_model.h5')
            #self.model = load_model(f'/media/data/sm2/smartmirror2/data{os.sep}gestures_model.h5')
            self.logger.info('The CNN has been loaded.')
        except Exception as error:
            self.model = None
            self.logger.error(f'Cannot load the CNN: {error}')

        frame_counter = 0
        while self.camera.isOpened():
            try:
                ret, frame = self.camera.read()

                if ret:
                    frame = cv2.flip(frame, 1)

                    frame = cv2.resize(frame, (640,480))

                    roi = frame[self.begin_Y:self.end_Y, self.begin_X:self.end_X]

                    fgmask = self.background_substractor.apply(roi, learningRate=0.00005)

                    # Get rid of noise
                    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, self.kernel)

                    # Dilation of the foreground
                    fgmask = cv2.dilate(fgmask, self.dilation_kernel, iterations = 3)

                    self.predictor(frame, fgmask)

                    if self.queue:
                        self.queue.put({'detected_gesture' : self.predicted_gesture})

                    if __name__ == '__main__':
                        cv2.imshow('Camera capture', frame)
                        cv2.imshow('Foreground', fgmask)

                        k = cv2.waitKey(int(1))
                        if k == 27:    # Esc key to stop
                            break
                else:
                    break
            except Exception as exc:
                self.logger.critical(f'Cannot process current video frame: {exc}')

if __name__ == '__main__':
    try:
        g = GesturesRecognizer()
        g.tracker()
    except KeyboardInterrupt:
        g.camera.release()

__version__ = '0.96' # 10th September 2020
__author__ = 'Dmitry Kudryashov'
__maintainer__ = 'Dmitry Kudryashov'
__email__ = "dmitry-kud@yandex.ru"
__status__ = "Development"