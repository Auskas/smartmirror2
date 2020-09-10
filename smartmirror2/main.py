#!/usr/bin/python3
# main.py - the main module for my smart mirror project.

import sys
if sys.version_info[0] < 3:
    raise Exception("Python 3 required to run the script!")
import os, time, json
import asyncio
from tkinter import *

import logging

import socket

from widgets.clock import Clock
from widgets.calendar2 import Calendar
from widgets.covid import Covid
from widgets.stocks import Stocks
from widgets.youtube import YoutubePlayer
from widgets.ticker import Ticker
from widgets.loading import Loading
from scraper import Scraper

class Mirror():

    def __init__(self, asyncloop):
        self.logger = logging.getLogger('SM')
        self.logger.setLevel(logging.DEBUG)

        logFileHandler = logging.FileHandler(f'sm.log')
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
        with open(f'{self.HOME_DIR}{os.sep}widgets.json', encoding='utf-8') as widgets_config_file:
            self.WIDGETS_CONFIG = json.load(widgets_config_file)
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

        self.create_loading_window()
        self.loading = Loading(self.loading_window)

        for widget_id in self.WIDGETS_CONFIG.keys():
            if self.WIDGETS_CONFIG[widget_id]["show"]:
                name = self.WIDGETS_CONFIG[widget_id]["name"]
                params = self.widget_init(widget_id)
                if name == 'clock':
                    self.clock = Clock(
                        self.window,
                        relx=params[0],
                        rely=params[1],
                        width=params[2],
                        height=params[3],
                        anchor=params[4]
                    )
                    self.widgets[name] = self.clock
                elif name == 'calendar':
                    self.calendar = Calendar(
                        self.window,
                        relx=params[0],
                        rely=params[1],
                        width=params[2],
                        height=params[3],
                        anchor=params[4]
                    )
                    self.widgets[name] = self.calendar
                elif name == 'covid':
                    self.covid = Covid(
                        self.window,
                        relx=params[0],
                        rely=params[1],
                        width=params[2],
                        height=params[3],
                        anchor=params[4]
                    )
                    self.widgets[name] = self.covid
                elif name == 'stocks':
                    self.stocks = Stocks(
                        self.window,
                        relx=params[0],
                        rely=params[1],
                        width=params[2],
                        height=params[3],
                        anchor=params[4]
                    )
                    self.widgets[name] = self.stocks

                elif name == 'youtube':
                    self.youtube = YoutubePlayer(
                        self.window,
                        relx=params[0],
                        rely=params[1],
                        width=params[2],
                        height=params[3],
                        anchor=params[4]
                    )
                    #self.youtube.play()
                    self.widgets[name] = self.youtube

                elif name == 'ticker':
                    self.ticker = Ticker(
                        self.window,
                        relx=params[0],
                        rely=params[1],
                        width=params[2],
                        height=params[3],
                        anchor=params[4]
                    )
                    self.widgets[name] = self.ticker
        self.scraper = Scraper(asyncloop)

        self.loading_window.destroy()
        self.window.call("wm", "attributes", ".", "-topmost", "true")
        
        self.tasks = []
        self.tasks.append(self.loop.create_task(self.window_updater()))
        self.tasks.append(self.loop.create_task(self.manager()))
        self.tasks.append(
            self.loop.create_task(asyncio.start_server(self.cmd_from_web_cfg, '127.0.0.1', 9086))
        )

    def create_loading_window(self):
        self.loading_window = Toplevel()
        self.loading_window.title('Loading...')
        self.loading_window.configure(bg='black')
        self.loading_window.geometry("%dx%d+0+0" % (self.window_width, self.window_height))
        #self.loading_window.overrideredirect(True)
        self.loading_window.lift(self.window)

    def widget_init(self, widget_id):
        return (
            round(self.WIDGETS_CONFIG[widget_id]['relx'] / 100, 2),
            round(self.WIDGETS_CONFIG[widget_id]['rely'] / 100, 2),
            round(self.WIDGETS_CONFIG[widget_id]['width'] / 100, 2),
            round(self.WIDGETS_CONFIG[widget_id]['height'] / 100, 2),
            self.WIDGETS_CONFIG[widget_id]['anchor']
        )

    async def cmd_from_web_cfg(self, reader, writer):
        while True:
            data = (await reader.read(1024)).decode('utf8')
            if not data:
                break
            try:
                widgets = json.loads(data)
                with open(f'{self.HOME_DIR}{os.sep}widgets.json', 'r', encoding='utf-8') as widgets_config_file:
                    self.WIDGETS_CONFIG = json.load(widgets_config_file)
                for widget in widgets:
                    widget_id = widget[7:]
                    self.WIDGETS_CONFIG[widget_id]['relx'] = widgets[widget]['relx']
                    self.WIDGETS_CONFIG[widget_id]['rely'] = widgets[widget]['rely']
                    self.WIDGETS_CONFIG[widget_id]['width'] = widgets[widget]['width']
                    self.WIDGETS_CONFIG[widget_id]['height'] = widgets[widget]['height']

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
                    self.create_loading_window()
                    self.loading = Loading(self.loading_window)
                    for widget in self.WIDGETS_CONFIG.keys():
                        if self.WIDGETS_CONFIG[widget]['show']:
                            self.widgets[self.WIDGETS_CONFIG[widget]['name']].show = True
                            self.widgets[self.WIDGETS_CONFIG[widget]['name']].update(
                                round(self.WIDGETS_CONFIG[widget]['relx'] / 100, 2),
                                round(self.WIDGETS_CONFIG[widget]['rely'] / 100, 2),
                                round(self.WIDGETS_CONFIG[widget]['width'] / 100, 2),
                                round(self.WIDGETS_CONFIG[widget]['height'] / 100, 2),
                                self.WIDGETS_CONFIG[widget]['anchor']
                            )
                        else:
                            self.widgets[self.WIDGETS_CONFIG[widget]['name']].show = False
                    self.loading_window.destroy()
                self.covid.covid_figures = self.scraper.covid_figures   
                self.stocks.rates_string = self.scraper.rates_string   
                self.ticker.news_string = self.scraper.news_string

                        
            except Exception as exc:
                self.logger.error(f'Cannot update the window {exc}')
            await asyncio.sleep(1)
    
    def close(self):
        try:
            self.logger.info('Closing mirror...')
            for task in self.tasks:
                task.cancel()
        except Exception as exc:
            self.logger(f'Cannot close the mirror: {exc}')

if __name__ == '__main__':
    try:
        asyncloop = asyncio.get_event_loop()
        mirror = Mirror(asyncloop)
        asyncloop.run_forever()
    except KeyboardInterrupt:
        mirror.close()

        