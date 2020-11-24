#!/usr/bin/python3
# weather.py - a weather widget for my Smart Mirror project.
# Environment variable "YANDEX_WEATHER_TOKEN" must be set to use the weather data.

from tkinter import *
import requests
import datetime
import logging
import os
from PIL import Image, ImageTk

class Weather:

    def __init__(self, window, relx=0.05, rely=0.05, width=0.2, height=0.2, anchor='nw', show=True):
        self.logger = logging.getLogger('SM2.weather')

        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)

        self.logger.info('Initialization of WEATHER widget...')

        self.SM2_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.ICONS_DIR = f'{self.SM2_DIR}{os.sep}icons{os.sep}weather{os.sep}'

        self.wind = {'nw': 'северо-западный', 'n': 'северный', 's': 'южный', 'w': 'западный',
                     'e': 'востончый', 'ne': 'северо-восточный', 'sw': 'юго-западный', 'se': 'юго-восточный'}

        self.window = window

        # Dimesnsions of the main window (screen size)
        self.window_width = window.winfo_screenwidth()
        self.window_height = window.winfo_screenheight()
        self.relx = relx
        self.rely = rely
        self.anchor = anchor
        self.show = show
        self.target_width = int(width * self.window_width)
        self.target_height = int(height * self.window_height)

        self.font_size = 50
        # The main frame of the widget.
        self.weather_frame = Frame(self.window, bg='black', bd=0)

        if self.anchor == 'ne':
            self.relx += width
        self.weather_frame.place(
            relx=self.relx,
            rely=self.rely,
            anchor=self.anchor)

        # The inner top frame with the name of the city.
        self.topframe_inside = Frame(self.weather_frame, bg='black', bd=0)
        self.topframe_inside.grid(column=0, row=0, sticky=self.anchor)

        # The inner bottom frame where all the weather data is displayed.
        self.bottomframe_inside = Frame(self.weather_frame, bg='black', bd=0)
        self.bottomframe_inside.grid(column=0, row=1, sticky=self.anchor)

        self.title_label = Label(self.topframe_inside, text="Москва", fg='lightblue', bg='black', font=("SFUIText", self.font_size, "bold"))
        if self.anchor == 'nw':
            self.title_label.pack(side=LEFT)
        else:
            self.title_label.pack(side=RIGHT)

        # The icon of the current weather taken from the self.ICONS_DIR folder.
        # It is placed the leftmost inside the inner bottom frame.
        self.icon_file = Image.open(f'{self.ICONS_DIR}bkn_+ra_d.png')
        icon_file_resized = self.icon_file.resize((int(self.font_size * 2), int(self.font_size * 2)), Image.ANTIALIAS)
        self.icon_render = ImageTk.PhotoImage(icon_file_resized)
        self.icon = Label(self.bottomframe_inside, image=self.icon_render, bg='black')
        self.icon.image = self.icon_render
        self.icon.pack(side=LEFT)

        # The current temperature frame placed to the right of the weather icon.
        self.degrees = Label(self.bottomframe_inside, text="-5°C", fg='lightblue', bg='black', font=("SFUIText", self.font_size, "bold"))
        self.degrees.pack(side=LEFT)
        # The forecast frame that is placed to the right of the current temperature frame.
        self.next_frame = Frame(self.bottomframe_inside, bg='black', bd=0)
        self.next_frame.pack(side=LEFT)

        # The top frame inside the forecast frame where the next period temperature is displayed.
        self.next_frame_top = Frame(self.next_frame, bg='black', bd=0)
        self.next_frame_top.grid(column=0, row=0, sticky=self.anchor)

        # The bottom frame inside the forecast frame where the second upcoming temperature period is shown.
        self.next_frame_bottom = Frame(self.next_frame, bg='black', bd=0)
        self.next_frame_bottom.grid(column=0, row=1, sticky=self.anchor)

        self.next_forecast = Label(self.next_frame_top, text="Днём -3°C", fg='lightblue', bg='black', font=("SFUIText", int(self.font_size / 2), "bold"))
        if self.anchor == 'w':
            self.next_forecast.pack(side = LEFT)
        else:
            self.next_forecast.pack(side = RIGHT)

        self.next_next_forecast = Label(self.next_frame_bottom, text="Вечером -6°C", fg='lightblue', bg='black', font=("SFUIText", int(self.font_size / 2), "bold"))
        if self.anchor == 'w':
            self.next_next_forecast.pack(side = LEFT)
        else:
            self.next_next_forecast.pack(side = RIGHT)

        self.forecast_string = None
        self.april_fools_forecast = {
            'fact': {'temp': -1, 'icon': 'fct_+sn'},
            'forecast': {
                'parts': {
                    'day': { 
                        'temp_avg': -5
                    },
                    'evening': {
                        'temp_avg': -8, 'part_name': 'night'
                    }
                }
            }
        }
        self.window.update_idletasks()
        self.get_font_size()
        self.logger.debug('WEATHER widget has been initialized.')
        self.status()

    def get_font_size(self):
        """ The method decreases the font size until it satisfies the target
            width and height of the widget."""
        while self.font_size > 12:
            self.title_label.config(font=("SFUIText", self.font_size // 2, "bold"))

            icon_file_resized = self.icon_file.resize((int(self.font_size * 1.5), int(self.font_size * 1.5)), Image.ANTIALIAS)
            self.icon_render = ImageTk.PhotoImage(icon_file_resized)
            self.icon.configure(image=self.icon_render)

            self.degrees.config(font=("SFUIText", self.font_size , "bold"))

            self.next_forecast.config(font=("SFUIText", self.font_size // 3, "bold"))

            self.next_next_forecast.config(font=("SFUIText", self.font_size // 3, "bold"))

            self.window.update_idletasks()

            self.weather_frame_width = self.weather_frame.winfo_width()
            self.weather_frame_height = self.weather_frame.winfo_height()

            if self.weather_frame_width > self.target_width or self.weather_frame_height > self.target_height:
                self.font_size -= 1
            else:
                #self.logger.debug(f'Target widget width {self.target_width}')
                #self.logger.debug(f'Real widget width {int(self.weather_frame_width)}')
                #self.logger.debug(f'Target widget height {self.target_height}')
                #self.logger.debug(f'Real widget height {int(self.weather_frame_height)}')
                break


    def status(self):
        if self.show and self.forecast_string is not None:
            self.weather_frame.place(
                relx=self.relx,
                rely=self.rely,
                anchor=self.anchor
            )
            self.widget()
        else:
            self.weather_frame.place_forget()
            self.weather_frame.after(1000, self.status)

    def widget(self):
        try:
            # Special weather forecast for April Fools' Day.
            current_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
            if current_time.month == 4 and current_time.day == 1 and self.seconds_counter > 3600:
                self.forecast_string = self.april_fools_forecast

            self.title_label.config(text='Москва')
            temp_now = str(self.forecast_string['fact']['temp'])
            weather_icon = self.forecast_string['fact']['icon']

            self.icon.configure(image=self.icon_render)
            #self.icon.image = self.icon_render

            # Gets the name of the next forecast periods.
            parts = set()
            try:
                for part in self.forecast_string['forecast']['parts'].keys():
                    parts.add(part)
            except AttributeError:
                parts.add(self.forecast_string['forecast']['parts'][0]['part_name'])
                parts.add(self.forecast_string['forecast']['parts'][1]['part_name'])

            if 'morning' in parts and 'day' in parts:
                part_next, part_next_next = 'morning', 'day'
            elif 'day' in parts and 'evening' in parts:
                part_next, part_next_next = 'day', 'evening'
            elif 'evening' in parts and 'night' in parts:
                part_next, part_next_next = 'evening', 'night'
            elif 'night' in parts and 'morning' in parts:
                part_next, part_next_next = 'night', 'morning'
            else:
                part_next, part_next_next = False, False

            if part_next:
                try:
                    temp_next = str(self.forecast_string['forecast']['parts'][part_next]['temp_avg'])
                except TypeError:
                    temp_next = str(self.forecast_string['forecast']['parts'][0]['temp_avg'])
            if part_next_next:
                try:
                    temp_next_next = str(self.forecast_string['forecast']['parts'][part_next_next]['temp_avg'])
                except TypeError:
                    temp_next_next = str(self.forecast_string['forecast']['parts'][1]['temp_avg'])

            # The following conditions are for determining the names of the next two part of a day.
            if part_next == 'night':
                part_next, part_next_next  = 'Ночью', 'утром'
            elif part_next == 'morning':
                part_next, part_next_next  = 'Утром', 'днём'
            elif part_next == 'day':
                part_next, part_next_next  = 'Днём', 'вечером'
            elif part_next == 'evening':
                part_next, part_next_next  = 'Вечером', 'ночью'
            else:
                part_next, part_next_next  = '', ''

            self.degrees.config(text=f'{temp_now}° ')
            self.next_forecast.config(text=f'{part_next} {temp_next},')
            self.next_next_forecast.config(text=f'{part_next_next} {temp_next_next}')
        except Exception as exc:
            self.logger.error(f'Cannot form the forecast strings: {exc}')
        self.weather_frame.after(1000, self.status)

    def widget_update(self, *args):
        try:
            self.logger.debug('Updating Weather widget...')
            self.relx = args[0]
            self.rely = args[1]
            self.weather_frame.place(relx=self.relx, rely=self.rely)
            width = args[2]
            height = args[3]
            self.anchor = args[4]
            if self.anchor == 'ne':
                self.relx += width
            self.target_width = int(width * self.window_width)
            self.target_height = int(height * self.window_height)
            self.font_size = 50

            self.weather_frame.place(
                relx=self.relx,
                rely=self.rely,
                anchor=self.anchor
            )
            
            self.get_font_size()
            self.topframe_inside.grid(
                column=0,
                row=0,
                sticky=self.anchor
            )

            self.bottomframe_inside.grid(
                column=0,
                row=1,
                sticky=self.anchor
            )

            self.next_frame_top.grid(
                column=0,
                row=0,
                sticky=self.anchor
            )

            self.next_frame_bottom.grid(
                column=0,
                row=1,
                sticky=self.anchor
            )

            if self.anchor == 'nw':
                self.title_label.pack(side=LEFT)
                self.next_forecast.pack(side = LEFT)
                self.next_next_forecast.pack(side = LEFT)
            else:
                self.title_label.pack(side=RIGHT)
                self.next_forecast.pack(side = RIGHT)
                self.next_next_forecast.pack(side = RIGHT)
            self.logger.debug('Widget has been updated!')
        except Exception as exc:
            self.logger.error(f'Cannot update the widget: {exc}')

    def destroy(self):
        self.logger.debug('Closing Weather...')
        self.weather_frame.destroy()

if __name__ == '__main__':
    window = Tk()
    window.title('Main Window')
    window.configure(bg='black')
    #window.overrideredirect(True)
    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    window.geometry("%dx%d+0+0" % (w, h))
    a = Weather(window)
    a.forecast_string = a.april_fools_forecast
    window.mainloop()

__version__ = '0.97' # 19th November 2020
__author__ = 'Dmitry Kudryashov'
__maintainer__ = 'Dmitry Kudryashov'
__email__ = "dmitry-kud@yandex.ru"
__status__ = "Development"
