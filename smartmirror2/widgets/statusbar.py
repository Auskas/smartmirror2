#!/usr/bin/python3
# statusbar.py - creates a widget that shows the temperature of the RPI and the IP address if it is assigned.

import os, sys
from tkinter import *
import datetime
import time
import logging

class Statusbar:

    def __init__(self, window, relx=0.05, rely=0.55, width=0.1, height=0.1, anchor='nw'):
        self.logger = logging.getLogger('SM.statusbar')

        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)

        self.window = window
        # Dimesnsions of the main window (screen size)
        self.window_width = window.winfo_screenwidth()
        self.window_height = window.winfo_screenheight()

        self.relx = relx
        self.rely = rely
        self.target_width = int(width * self.window_width)
        self.target_height = int(height * self.window_height)
        self.anchor = anchor

        self.font_size = 50

        self.statusbar_frame = Frame(self.window, bg='black', bd=0)

        if self.anchor == 'ne':
            self.relx += width

        self.statusbar_frame.place(
            relx=self.relx,
            rely=self.rely,
            anchor=self.anchor)

        # The inner top frame is used to display the CPU temperature.
        self.topframe_inside = Frame(self.statusbar_frame, bg='black', bd=0)
        self.topframe_inside.grid(column=0, row=0, sticky=self.anchor)

        # The inner middle frame is used to display the GPU temperature.
        self.middleframe_inside = Frame(self.statusbar_frame, bg='black', bd=0)
        self.middleframe_inside.grid(column=0, row=1, sticky=self.anchor)

        # The inner bottom frame is used to display the IP address.
        self.bottomframe_inside = Frame(self.statusbar_frame, bg='black', bd=0)
        self.bottomframe_inside.grid(column=0, row=2, sticky=self.anchor)

        self.temp_CPU = ''
        self.temp_GPU = ''
        self.IP_address = ''

        self.cpu_temp_label = Label(
            self.topframe_inside,
            text='CPU 21 °C',
            fg='lightblue',
            bg='black',
            font=("SFUIText", self.font_size, "bold")
        )

        self.gpu_temp_label = Label(
            self.middleframe_inside,
            text='GPU 22 °C',
            fg='lightblue',
            bg='black',
            font=("SFUIText", self.font_size, "bold")
        )

        self.ip_address_label = Label(
            self.bottomframe_inside,
            text='000.000.000.000',
            fg='lightblue',
            bg='black',
            font=("SFUIText", self.font_size, "bold")
        )
        if self.anchor == 'nw':
            self.cpu_temp_label.pack(side=LEFT)
        else:
            self.cpu_temp_label.pack(side=RIGHT)

        if self.anchor == 'nw':
            self.gpu_temp_label.pack(side=LEFT)
        else:
            self.gpu_temp_label.pack(side=RIGHT)

        if self.anchor == 'nw':
            self.ip_address_label.pack(side=LEFT)
        else:
            self.ip_address_label.pack(side=RIGHT)

        self.window.update_idletasks()
        self.get_font_size()

        self.logger.info('Clock widgets has been created.')
        self.show = True
        self.status()

    def get_font_size(self):
        """ The method decreases the font size until it satisfies the target
            width and height of the widget."""
        while self.font_size > 12:
            self.cpu_temp_label.config(font=("SFUIText", self.font_size, "bold"))
            self.gpu_temp_label.config(font=("SFUIText", self.font_size, "bold"))
            self.ip_address_label.config(font=("SFUIText", self.font_size, "bold"))

            self.window.update_idletasks()

            self.statusbar_frame_width = self.statusbar_frame.winfo_width()
            self.statusbar_frame_height = self.statusbar_frame.winfo_height()
            if self.statusbar_frame_width > self.target_width or self.statusbar_frame_height > self.target_height:
                self.font_size -= 1
            else:
                self.logger.debug(f'Target widget width {self.target_width}')
                self.logger.debug(f'Real widget width {int(self.statusbar_frame_width)}')
                self.logger.debug(f'Target widget height {self.target_height}')
                self.logger.debug(f'Real widget height {int(self.statusbar_frame_height)}')
                break

    def status(self):
        if self.show:
            self.statusbar_frame.place(
                relx=self.relx,
                rely=self.rely,
                anchor=self.anchor
            )
            self.widget()
        else:
            self.statusbar_frame.place_forget()
            self.statusbar_frame.after(1000, self.status)

    def widget(self):
        self.cpu_temp_label.config(text=self.temp_CPU)
        self.gpu_temp_label.config(text=self.temp_GPU)
        self.ip_address_label.config(text=self.IP_address)
        self.measure_temp()

    def measure_temp(self):
        try:
            self.temp_CPU = os.popen("cat /sys/class/thermal/thermal_zone0/temp").readline()
            self.temp_CPU = round(int(self.temp_CPU) / 1000, 1)
            self.temp_CPU = f'CPU {str(self.temp_CPU)}°C'
        except Exception as exc:
            self.temp_CPU = ''
            self.logger.error(f'Cannot get the CPU temp: {exc}')

        try:
            self.temp_GPU = os.popen("vcgencmd measure_temp").readline()
            self.temp_GPU = self.temp_GPU[self.temp_GPU.find('=') + 1: self.temp_GPU.find("'")]
            self.temp_GPU = float(self.temp_GPU)
            self.temp_GPU = f'GPU {self.temp_GPU}°C'
        except Exception as exc:
            self.logger.error(f'Cannot get the GPU temp: {exc}')

        try:
            self.IP_address = f'IP: {os.popen("hostname -I").readline()}'
        except Exception as exc:
            self.logger.error(f'Cannot get the IP address: {exc}')

        self.statusbar_frame.after(3000, self.status)

    def widget_update(self, *args):
        self.relx = args[0]
        self.rely = args[1]
        self.statusbar_frame.place(relx=self.relx, rely=self.rely)
        width = args[2]
        height = args[3]
        self.anchor = args[4]
        if self.anchor == 'ne':
            self.relx += width
        self.target_width = int(width * self.window_width)
        self.target_height = int(height * self.window_height)
        self.font_size = 50
        self.get_font_size()
        self.topframe_inside.grid(
            column=0,
            row=0,
            sticky=self.anchor
        )

        self.middleframe_inside.grid(
            column=0,
            row=1,
            sticky=self.anchor
        )

        self.bottomframe_inside.grid(
            column=0,
            row=2,
            sticky=self.anchortitle_label
        )

        if self.anchor == 'nw':
            self.cpu_temp_label.pack(side=LEFT)
            self.gpu_temp_label.pack(side = LEFT)
            self.ip_address_label.pack(side = LEFT)
        else:
            self.cpu_temp_label.pack(side=RIGHT)
            self.gpu_temp_label.pack(side = RIGHT)
            self.ip_address_label.pack(side = RIGHT)


if __name__ == '__main__':
    try:
        window = Tk()
        window.title('Main Window')
        window.configure(bg='black')
        #window.overrideredirect(True)
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry("%dx%d+0+0" % (w, h))
        a = Statusbar(window)
        window.mainloop()
    except KeyboardInterrupt:
        sys.exit()

__version__ = '0.1' # 7th November 2020
__author__ = 'Dmitry Kudryashov'
__maintainer__ = 'Dmitry Kudryashov'
__email__ = "dmitry-kud@yandex.ru"
__status__ = "Development"