#!/usr/bin/python3
# main.py - the main module for my smart mirror project.

import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 required to run the script!")
import os, time, json
import asyncio
from tkinter import *

import logging

import re

import subprocess

import cv2

from multiprocessing import Process, Queue

from widgets.clock import Clock
from widgets.calendar2 import Calendar
from widgets.covid import Covid
from widgets.stocks import Stocks
from widgets.youtube import YoutubePlayer
from widgets.ticker import Ticker
from widgets.weather import Weather
from widgets.loading import Loading
from widgets.statusbar import Statusbar
from widgets.gestures_widget import GesturesWidget
from widgets.voice_assistant_widget import VoiceAssistantWidget
from scraper import Scraper
from gestures import GesturesRecognizer
from voice_assistant import VoiceAssistant
#from test_cmd import TestCMD

class Mirror():

    def __init__(self, asyncloop):
        self.logger = logging.getLogger('SM')
        self.logger.setLevel(logging.DEBUG)

        logFileHandler = logging.FileHandler(f'sm2.log')
        logFileHandler.setLevel(logging.DEBUG)

        logConsole = logging.StreamHandler()
        logConsole.setLevel(logging.DEBUG)

        formatterFile = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        formatterConsole = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        logFileHandler.setFormatter(formatterFile)
        logConsole.setFormatter(formatterConsole)

        self.logger.addHandler(logFileHandler)
        self.logger.addHandler(logConsole)

        logging.getLogger("requests").setLevel(logging.WARNING)
        logging.getLogger("urllib3").setLevel(logging.WARNING)

        self.logger.info('########## MIRROR STARTED ##########')
        self.HOME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.logger.debug(f'Home directory is {self.HOME_DIR}')

        try:
            host_ip_address = f'IP: {os.popen("hostname -I").readline()}'
            ip_address_regex = re.compile(r'(\d)+.(\d)+.(\d).+(\d)')
            self.IP_ADDRESS = ip_address_regex.search(host_ip_address)
            if self.IP_ADDRESS is not None:
                self.SERVER_IP_ADDRESS = self.IP_ADDRESS.group()
                self.SERVER_PORT = 9086
                self.logger.info(f'Host IP address is {self.SERVER_IP_ADDRESS}')
            else:
                self.SERVER_IP_ADDRESS = 'localhost'
                self.SERVER_PORT = 9086
                self.logger.warning(f'IP address has not been assigned to the host! Using localhost...')
        except Exception as exc:
            self.logger.error(f'Cannot get the IP address: {exc}')

        # Web server initialization
        try:
            if self.SERVER_IP_ADDRESS == 'localhost':
                os.popen(f'python3 {self.HOME_DIR}{os.sep}web{os.sep}manage.py runserver')
            else:
                os.popen(f'python3 {self.HOME_DIR}{os.sep}web{os.sep}manage.py runserver {self.SERVER_IP_ADDRESS}:{self.SERVER_PORT}')
            self.logger.info('Successfully initialized the web server!')
        except Exception as exc:
            self.logger.error(f'Cannot start the web server: {exc}')
        try:
            with open(f'{self.HOME_DIR}{os.sep}widgets.json', encoding='utf-8') as widgets_config_file:
                self.WIDGETS_CONFIG = json.load(widgets_config_file)
            self.logger.debug('Widgets conf file has been read!')
        except Exception as exc:
            self.logger.exception('Cannot open widget config file!')

        if os.environ.get('DISPLAY','') == '':
            self.logger.debug('no display found. Using :0.0')
            os.environ.__setitem__('DISPLAY', ':0.0')

        try:
            self.loop = asyncloop

            self.widgets = {}

            self.update_widgets = False

            self.window = Tk()
            self.window.title('Smart Mirror Mark II')
            self.window.configure(bg='black')
            # Disables closing the window by standard means, such as ALT+F4 etc.
            #self.window.overrideredirect(True)
            self.window_width = self.window.winfo_screenwidth()
            self.window_height = self.window.winfo_screenheight()
            self.window.geometry("%dx%d+0+0" % (self.window_width, self.window_height))
            self.logger.info('Main window has been created')

        except Exception as exc:
            self.logger.exception('Cannot create the main window!')

        self.create_loading_window()
        self.loading = Loading(self.loading_window)

        self.queue = Queue()

        # Checks if there is a camera device on board.
        self.cam = cv2.VideoCapture(0)
        if self.cam is None or not self.cam.isOpened():
            self.gestures_recognizer = False
            self.logger.info('No camera device has been found on board.')
        else:
            self.gestures_recognizer = GesturesRecognizer(self.cam, self.queue)
            self.gestures_recognizer_process = Process(target=self.gestures_recognizer.tracker).start()
            self.logger.info('A camera device has been found on board.')

        # Initialization of every available widget.
        for widget_name in self.WIDGETS_CONFIG.keys():
            params = self.widget_init(widget_name)

            if widget_name == 'youtube':
                self.youtube = YoutubePlayer(
                    self.window,
                    asyncloop,
                    relx=params[0],
                    rely=params[1],
                    width=params[2],
                    height=params[3],
                    anchor=params[4],
                    default_video=params[5]
                )
                self.widgets[widget_name] = self.youtube

            elif widget_name == 'clock':
                self.clock = Clock(
                    self.window,
                    relx=params[0],
                    rely=params[1],
                    width=params[2],
                    height=params[3],
                    anchor=params[4]
                )
                self.widgets[widget_name] = self.clock
            elif widget_name == 'calendar':
                self.calendar = Calendar(
                    self.window,
                    relx=params[0],
                    rely=params[1],
                    width=params[2],
                    height=params[3],
                    anchor=params[4]
                )
                self.widgets[widget_name] = self.calendar
            elif widget_name == 'covid':
                self.covid = Covid(
                    self.window,
                    relx=params[0],
                    rely=params[1],
                    width=params[2],
                    height=params[3],
                    anchor=params[4]
                )
                self.widgets[widget_name] = self.covid
            elif widget_name == 'stocks':
                self.stocks = Stocks(
                    self.window,
                    relx=params[0],
                    rely=params[1],
                    width=params[2],
                    height=params[3],
                    anchor=params[4]
                )
                self.widgets[widget_name] = self.stocks

            elif widget_name == 'ticker':
                self.ticker = Ticker(
                    self.window,
                    relx=params[0],
                    rely=params[1],
                    width=params[2],
                    height=params[3],
                    anchor=params[4]
                )
                self.widgets[widget_name] = self.ticker
            elif widget_name == 'weather':
                self.weather = Weather(
                    self.window,
                    relx=params[0],
                    rely=params[1],
                    width=params[2],
                    height=params[3],
                    anchor=params[4]
                )
                self.widgets[widget_name] = self.weather
            elif widget_name == 'voice_assistant':
                self.voice_assistant_widget = VoiceAssistantWidget(
                    self.window,
                    relx=params[0],
                    rely=params[1],
                    width=params[2],
                    height=params[3],
                    anchor=params[4]
                )
                self.widgets[widget_name] = self.voice_assistant_widget
            elif widget_name == 'statusbar':
                self.statusbar = Statusbar(
                    self.window,
                    relx=params[0],
                    rely=params[1],
                    width=params[2],
                    height=params[3],
                    anchor=params[4]
                )
                self.widgets[widget_name] = self.statusbar
            elif widget_name == 'gestures':
                self.gestures_widget = GesturesWidget(
                    self.window,
                    relx=params[0],
                    rely=params[1],
                    width=params[2],
                    height=params[3],
                    anchor=params[4]
                )
                self.widgets[widget_name] = self.gestures_widget
        for widget_name in self.widgets:
            if self.WIDGETS_CONFIG[widget_name]['show']:
                self.widgets[widget_name].show = True
            else:
                self.widgets[widget_name].show = False

        self.scraper = Scraper(asyncloop)

        self.loading_window.destroy()
        self.window.call("wm", "attributes", ".", "-topmost", "true")

        self.gesture = False
        self.user_detected = False
        self.voice_command = []

        self.voice_assistant = VoiceAssistant(self.WIDGETS_CONFIG, self.queue)

        self.tasks = []
        self.tasks.append(self.loop.create_task(self.window_updater()))
        self.tasks.append(self.loop.create_task(self.manager()))
        self.tasks.append(
            self.loop.create_task(
                asyncio.start_server(
                    self.cmd_from_web_cfg,
                    #self.SERVER_IP_ADDRESS,
                    'localhost',
                    self.SERVER_PORT
                )
            )
        )
        self.tasks.append(self.loop.create_task(self.process_receiver()))
        # For testing purposes only!
        #self.test_cmd = TestCMD(self.queue)
        #test_cmd_process = Process(target=self.test_cmd.send_command).start()
        self.gestures_to_command = {
            '5': 'Распознование голоса',
            '4': 'Четыре (не назначено)',
            'pointing_finger': 'Уменьшение громкости',
            'sign_of_the_horns': 'Увеличение громкости',
            'inverted_l': 'Следующее видео',
            'peace': 'Мир (не назначено)',
            'thumb_up': 'Большой палец вверх (не назначено)',
            False: 'НЕТ'
        }

    def create_loading_window(self):
        self.loading_window = Toplevel()
        self.loading_window.title('Loading...')
        self.loading_window.configure(bg='black')
        self.loading_window.geometry("%dx%d+0+0" % (self.window_width, self.window_height))
        #self.loading_window.overrideredirect(True)
        self.loading_window.lift(self.window)

    def widget_init(self, widget_name):
        if widget_name == 'youtube':
            default_video = self.WIDGETS_CONFIG[widget_name]['defaultVideo']
        else:
            default_video = False
        return (
            round(self.WIDGETS_CONFIG[widget_name]['relx'] / 100, 5),
            round(self.WIDGETS_CONFIG[widget_name]['rely'] / 100, 5),
            round(self.WIDGETS_CONFIG[widget_name]['width'] / 100, 5),
            round(self.WIDGETS_CONFIG[widget_name]['height'] / 100, 5),
            self.WIDGETS_CONFIG[widget_name]['anchor'],
            default_video
        )

    async def cmd_from_web_cfg(self, reader, writer):
        while True:
            data = (await reader.read(4096)).decode('utf8')
            if not data:
                break
            try:
                widgets = json.loads(data)
                with open(f'{self.HOME_DIR}{os.sep}widgets.json', 'r', encoding='utf-8') as widgets_config_file:
                    self.WIDGETS_CONFIG = json.load(widgets_config_file)
                for widget in widgets.keys():

                    widget_name = widget[7:]
                    if widgets[widget]['show'] == False:
                        self.WIDGETS_CONFIG[widget_name]['show'] = widgets[widget]['show']
                    else:
                        self.WIDGETS_CONFIG[widget_name]['relx'] = float(widgets[widget]['relx'])
                        self.WIDGETS_CONFIG[widget_name]['rely'] = float(widgets[widget]['rely'])
                        self.WIDGETS_CONFIG[widget_name]['width'] = float(widgets[widget]['width'])
                        self.WIDGETS_CONFIG[widget_name]['height'] = float(widgets[widget]['height'])
                        self.WIDGETS_CONFIG[widget_name]['show'] = widgets[widget]['show']
                        self.WIDGETS_CONFIG[widget_name]['anchor'] = widgets[widget]['anchor']
                    # Special key for YouTube widget.
                    if widget_name == 'youtube':
                        self.WIDGETS_CONFIG[widget_name]['defaultVideo'] = widgets[widget]['defaultVideo']
                self.update_widgets = True
                with open(f'{self.HOME_DIR}{os.sep}widgets.json', 'w', encoding='utf-8') as widgets_config_file:
                    json.dump(self.WIDGETS_CONFIG, widgets_config_file, indent=2)

            except Exception as exc:
                self.logger.error(f'Cannot get and decode the json web server message: {exc}')
        writer.close()

    async def window_updater(self):
        interval = 1/120
        while True:
            self.window.update()
            await asyncio.sleep(interval)

    async def manager(self):
        while True:
            try:
                if self.update_widgets:
                    self.update_widgets = False

                    # Temporaly stops Gestures Recognizer while updating the widgets.
                    if self.gestures_recognizer:
                        self.gestures_recognizer.show = False

                    self.create_loading_window()
                    self.loading = Loading(self.loading_window)
                    for widget in self.WIDGETS_CONFIG.keys():
                        if self.WIDGETS_CONFIG[widget]['show']:
                            if widget == 'youtube':
                                default_video = self.WIDGETS_CONFIG[widget]['defaultVideo']
                            else:
                                default_video = None
                            self.widgets[self.WIDGETS_CONFIG[widget]['name']].show = True
                            self.widgets[self.WIDGETS_CONFIG[widget]['name']].widget_update(
                                round(self.WIDGETS_CONFIG[widget]['relx'] / 100, 5),
                                round(self.WIDGETS_CONFIG[widget]['rely'] / 100, 5),
                                round(self.WIDGETS_CONFIG[widget]['width'] / 100, 5),
                                round(self.WIDGETS_CONFIG[widget]['height'] / 100, 5),
                                self.WIDGETS_CONFIG[widget]['anchor'],
                                default_video
                            )
                        else:
                            self.widgets[self.WIDGETS_CONFIG[widget]['name']].show = False
                    self.loading_window.destroy()
                    if self.gestures_recognizer:
                        self.gestures_recognizer.show = True

                if 'youtube' in self.widgets.keys():
                    if self.gesture == 'pointing_finger':
                        self.youtube.external_command = 'volume_down'
                    elif self.gesture == 'sign_of_the_horns':
                        self.youtube.external_command = 'volume_up'
                    elif self.gesture == 'inverted_l':
                        self.youtube.external_command = 'next_video'
                    elif self.gesture == None:
                        self.youtube.external_command = None

                if self.gesture == '5':
                    if self.voice_assistant_widget.show_wave == False:
                        voice_assistant_process = Process(target=self.voice_assistant.listen).start()
                        self.youtube.mute()
                        self.voice_assistant_widget.show_wave = True
                        self.voice_assistant_widget.show_wave_widget()

                if self.scraper:
                    self.covid.covid_figures = self.scraper.covid_figures
                    self.stocks.rates_string = self.scraper.rates_string
                    self.ticker.news_string = self.scraper.news_string
                    self.weather.forecast_string = self.scraper.forecast_string

            except Exception as exc:
                self.logger.error(f'Cannot update the window {exc}')

            await asyncio.sleep(0.1)

    async def process_receiver(self):
        """ The method is asynchronously waits for strings in the queue."""
        while True:
            if self.queue.empty():
                await asyncio.sleep(1)
            else:
                data = self.queue.get()
                try:
                    for key in data.keys():
                        if key == 'detected_gesture':
                            if data[key] == None:
                                self.gesture = False
                                self.gestures_widget.detected_gesture = self.gestures_to_command[self.gesture]
                            else:
                                self.gesture = data[key]
                                self.gestures_widget.detected_gesture = self.gestures_to_command[self.gesture]
                        
                        # The following condition processes commands from the voice assistant module.
                        elif key == 'voice_assistant':
                            self.voice_assistant_widget.show_wave = False
                            self.youtube.unmute()
                            for cmd_key in data[key]:
                                if cmd_key == 'error' and data[key][cmd_key]:
                                    self.voice_assistant_widget.message = data[key][cmd_key]
                                    break
                                else:
                                    self.voice_assistant_widget.message = data[key]['raw_string']
                                if cmd_key == 'youtube_search' and data[key][cmd_key]:
                                    youtube_search_task = self.loop.create_task(self.youtube.search(data[key][cmd_key]))
                                elif cmd_key == 'youtube_play' and data[key][cmd_key]:
                                    self.youtube.play()
                                elif cmd_key == 'youtube_stop' and data[key][cmd_key]:
                                    self.youtube.stop()
                                elif cmd_key == 'youtube_pause' and data[key][cmd_key]:
                                    self.youtube.list_player.pause()
                                elif cmd_key == 'youtube_fullscreen' and data[key][cmd_key]:
                                    self.youtube.set_fullscreen()
                                elif cmd_key == 'youtube_window' and data[key][cmd_key]:
                                    self.youtube.set_window() 
                                elif cmd_key in self.WIDGETS_CONFIG.keys():
                                    self.WIDGETS_CONFIG[cmd_key]['show'] = data[key][cmd_key]   

                        elif key == 'face_detected':
                            self.face_detected = data[key]

                        else:
                            self.face_detected = False
                            self.gesture = False
                            self.gestures_widget.detected_gesture = self.gesture

                except Exception as exc:
                    self.logger.warning(f'Cannot process the data in the queue {exc}')

    def close(self):
        try:
            self.logger.info('Closing mirror...')
            for task in self.tasks:
                task.cancel()
            if self.cam is not None or self.cam.isOpened():
                self.cam.release()
        except Exception as exc:
            self.logger(f'Cannot close the mirror: {exc}')

if __name__ == '__main__':
    try:
        asyncloop = asyncio.get_event_loop()
        mirror = Mirror(asyncloop)
        asyncloop.run_forever()
    except KeyboardInterrupt:
        mirror.close()