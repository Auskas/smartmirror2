#!/usr/bin/python3
# gestures_widget.py - creates a widget that shows detected hand gestures.

import os, sys
from tkinter import *
import datetime
import time
import cv2
import logging

class GesturesWidget:

    def __init__(self, window, relx=0.05, rely=0.55, width=0.1, height=0.1, anchor='nw', show=True):
        self.logger = logging.getLogger('SM2.gestures_widget')

        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)

        self.logger.info('Initialization of GESTURES widget...')

        self.window = window
        # Dimesnsions of the main window (screen size)
        self.window_width = window.winfo_screenwidth()
        self.window_height = window.winfo_screenheight()

        self.relx = relx
        self.rely = rely
        self.target_width = int(width * self.window_width)
        self.target_height = int(height * self.window_height)
        self.anchor = anchor
        self.show = show

        self.font_size = 40

        self.gestures_frame = Frame(self.window, bg='black', bd=0)

        if self.anchor == 'ne':
            self.relx += width

        self.gestures_frame.place(
            relx=self.relx,
            rely=self.rely,
            anchor=self.anchor)

        self.detected_gesture = 'НЕТ'

        self.gestures_dict = {
            '5':'ПЯТЬ',
            '4':'ЧЕТЫРЕ',
            'inverted_l':'ИНВЕРТИРОВАННАЯ L',
            'peace':'МИР',
            'pointing_finger':'УКАЗАТЕЛЬНЫЙ ПАЛЕЦ',
            None:'НЕТ',
            False:'НЕТ',
            'sign_of_the_horns':'КОЗА',
            'thumb_up':'ОТЛИЧНО!'            
        }

        self.gestures_label = Label(
            self.gestures_frame,
            text='Указательный палец',
            fg='lightblue',
            bg='black',
            font=("SFUIText", self.font_size, "bold")
        )

        if self.anchor == 'nw':
            self.gestures_label.pack(side=LEFT)
        else:
            self.gestures_label.pack(side=RIGHT)

        self.window.update_idletasks()
        self.get_font_size()

        self.logger.info('GESTURES widget has been created.')
        self.status()

    def get_font_size(self):
        """ The method decreases the font size until it satisfies the target
            width and height of the widget."""
        while self.font_size > 12:
            self.gestures_label.config(font=("SFUIText", self.font_size, "bold"))

            self.window.update_idletasks()

            self.gestures_frame_width = self.gestures_frame.winfo_width()
            self.gestures_frame_height = self.gestures_frame.winfo_height()
            if self.gestures_frame_width > self.target_width or self.gestures_frame_height > self.target_height:
                self.font_size -= 1
            else:
                #self.logger.debug(f'Target widget width {self.target_width}')
                #self.logger.debug(f'Real widget width {int(self.gestures_frame_width)}')
                #self.logger.debug(f'Target widget height {self.target_height}')
                #self.logger.debug(f'Real widget height {int(self.gestures_frame_height)}')
                break

    def status(self):
        if self.show:
            self.gestures_frame.place(
                relx=self.relx,
                rely=self.rely,
                anchor=self.anchor
            )
            self.widget()
        else:
            self.gestures_frame.place_forget()
            self.gestures_frame.after(10, self.status)

    def widget(self):
        self.gestures_label.config(
            text=f'Жесты управления:\n{self.detected_gesture}'
        )

        self.gestures_frame.after(10, self.status)

    def widget_update(self, *args):
        try:
            self.logger.debug('Updating Gestures widget...')
            self.relx = args[0]
            self.rely = args[1]
            self.gestures_frame.place(relx=self.relx, rely=self.rely)
            width = args[2]
            height = args[3]
            self.anchor = args[4]
            if self.anchor == 'ne':
                self.relx += width
            self.target_width = int(width * self.window_width)
            self.target_height = int(height * self.window_height)
            self.font_size = 50

            self.gestures_frame.place(
                relx=self.relx,
                rely=self.rely,
                anchor=self.anchor
            )
            self.gestures_label.config(text='Указательный палец')

            self.get_font_size()

            if self.anchor == 'nw':
                self.gestures_label.pack(side=LEFT)
            else:
                self.gestures_label.pack(side=RIGHT)
            self.logger.debug('Widget has been updated!')
        except Exception as exc:
            self.logger.error(f'Cannot update the widget: {exc}')

    def destroy(self):
        self.logger.debug('Closing Gestures...')
        self.gestures_frame.destroy()

if __name__ == '__main__':
    try:
        window = Tk()
        window.title('Main Window')
        window.configure(bg='black')
        #window.overrideredirect(True)
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry("%dx%d+0+0" % (w, h))
        a = GesturesWidget(window)
        window.mainloop()
    except KeyboardInterrupt:
        sys.exit()

__version__ = '0.97' # 19th November 2020
__author__ = 'Dmitry Kudryashov'
__maintainer__ = 'Dmitry Kudryashov'
__email__ = "dmitry-kud@yandex.ru"
__status__ = "Development"