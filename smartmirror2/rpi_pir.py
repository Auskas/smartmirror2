#import libraries
import logging
import RPi.GPIO as GPIO
import time
import subprocess
import asyncio
from settings import *

class PIR:
    
    def __init__(self, asyncloop):
        self.logger = logging.getLogger('SM2.PIR')
        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)

        self.loop = asyncloop
        self.PIR_DELAY = PIR_DELAY
        self.motion_detected_first_time = time.perf_counter()
        
        self.PIR_TIMEOUT = PIR_TIMEOUT
        self.motion_detected_last_time = time.perf_counter()
        
        self.show = False
        
        self.REFRESH_RATE = 0.1 # seconds.
        
        self.PIRsensor = 4  # PIR sensor attached to the GPIO4

        GPIO.setmode(GPIO.BCM)  # Numbers GPIOs by BCM
        GPIO.setup(self.PIRsensor, GPIO.IN)

        pir_loop = self.loop.create_task(self.status())

        self.logger.info('PIR sensor instance has been initialized!')
        
    def change_display_mode(self, display_power=1):
        subprocess.Popen(
            f'vcgencmd display_power {display_power}',
            shell=True,
            stdout=subprocess.DEVNULL
        )        
    
    def get_sensor(self):
        return GPIO.input(self.PIRsensor)
    
    async def status(self):
        while True:
            self.current_state = self.get_sensor()
            if self.current_state == True:
                self.motion_detected_last_time = time.perf_counter()
                if self.motion_detected_first_time == False:
                    self.logger.debug('Initial motion detected')
                    self.motion_detected_first_time = time.perf_counter()
                if self.motion_detected_last_time - self.motion_detected_first_time > self.PIR_DELAY:
                
                    if self.show == False:
                        self.logger.debug('Motion detection delay has been fulfilled!')
                        self.change_display_mode()
                    self.show = True
            else:
                if self.motion_detected_first_time and time.perf_counter() - self.motion_detected_last_time > self.PIR_TIMEOUT:
                    self.logger.debug('Motion detection timeout!')
                    self.show = False
                    self.motion_detected_first_time = False
                    self.change_display_mode(0)
            await asyncio.sleep(self.REFRESH_RATE)

if __name__ == '__main__':
    import sys
    try:
        loop = asyncio.get_event_loop()
        sensor = PIR(loop)
        loop.run_forever()
    except KeyboardInterrupt:
        sys.exit()