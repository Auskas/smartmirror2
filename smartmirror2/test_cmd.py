from multiprocessing import Process, Queue
import socket
import json
import time

class TestCMD:

    def __init__(self, queue):
        self.test_command = {'voice_assistant': {'youtube_search': 'Corey Schafer Django'}}
        self.queue = queue

    def send_command(self):
        time.sleep(30)
        self.queue.put(self.test_command)

