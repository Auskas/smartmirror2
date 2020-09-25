from multiprocessing import Process, Queue
from gestures import GesturesRecognizer
import asyncio
import logging
import cv2
import multiprocessing
from tensorflow.keras.models import load_model
import os

#multiprocessing.set_start_method('spawn', force=True)

class Test:

    def __init__(self, asyncloop):
        self.logger = logging.getLogger('SM')
        self.logger.setLevel(logging.DEBUG)

        #logFileHandler = logging.FileHandler(f'sm.log')
        #logFileHandler.setLevel(logging.DEBUG)

        logConsole = logging.StreamHandler()
        logConsole.setLevel(logging.DEBUG)

        #formatterFile = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatterConsole = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        #logFileHandler.setFormatter(formatterFile)
        logConsole.setFormatter(formatterConsole)

        #self.logger.addHandler(logFileHandler)
        self.logger.addHandler(logConsole)

        self.loop = asyncloop

        self.queue = Queue()

        self.loop.create_task(self.process_receiver())

        self.cam = cv2.VideoCapture(0)
        

        if self.cam is None or not self.cam.isOpened():
            self.logger.info('No camera device has been found on board.')    
        else:
            self.gestures_recognizer = GesturesRecognizer(self.cam, self.queue)
            self.gestures_recognizer_process = Process(target=self.gestures_recognizer.tracker).start()
            self.logger.info('A camera device has been found on board.')

    async def process_receiver(self):
        """ The method is asynchronously waits for strings in the queue."""
        while True:
            if self.queue.empty():
                await asyncio.sleep(1)
            else:
                data = self.queue.get()
                try:
                    print(data)
                except Exception as exc:
                    self.logger.warning(f'Cannot process the data in the queue {exc}')    

if __name__ == '__main__':
    try:
        asyncloop = asyncio.get_event_loop()
        test = Test(asyncloop)
        asyncloop.run_forever()
    except KeyboardInterrupt:
        test.cam.release()