from multiprocessing import Process, Queue
from gestures import GesturesRecognizer
import asyncio
import logging
import cv2

camera = cv2.VideoCapture(0)
queue = False
g = GesturesRecognizer(camera, queue)
g.tracker()