#!/usr/bin/python3
# statusbar.py - creates a widget that shows the temperature of the RPI and the IP address if it is assigned.

import os, sys
import subprocess
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

        self.REFRESH_RATE = 10000 # time in milliseconds between measurments.

        self.window = window
        # Dimesnsions of the main window (screen size)
        self.window_width = window.winfo_screenwidth()
        self.window_height = window.winfo_screenheight()

        self.relx = relx
        self.rely = rely
        self.target_width = int(width * self.window_width)
        self.target_height = int(height * self.window_height)
        self.anchor = anchor

        self.font_size = 30

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

        self.temp_CPU = subprocess.Popen(
            'cat /sys/class/thermal/thermal_zone0/temp',
            shell=True, 
            stdin=None, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )

        _, temp_CPU_error = self.temp_CPU.communicate() 
        if temp_CPU_error.decode("utf-8").find('not found') != -1:
            self.logger.warning('CPU temperature measurment is not supported!')
            self.temp_CPU.stdout.close()
            self.temp_CPU = False
        else:
            self.temp_CPU = 'CPU __._°C'

        self.temp_GPU = subprocess.Popen(
            'vcgencmd measure_temp',
            shell=True, 
            stdin=None, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )

        _, temp_GPU_error = self.temp_GPU.communicate() 
        if temp_GPU_error.decode("utf-8").find('not found') != -1:
            self.logger.warning('GPU temperature measurement is not supported!')
            self.temp_GPU.stdout.close()
            self.temp_GPU = False
        else:
            self.temp_GPU = 'GPU __._°C'
        
        self.IP_address = subprocess.Popen(
            'hostname -I',
            shell=True, 
            stdin=None, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE
        )

        _, IP_address_error = self.IP_address.communicate() 
        if IP_address_error.decode("utf-8").find('not found') != -1:
            self.logger.warning('Cannot get the IP address!')
            self.IP_address.stdout.close()
            self.IP_address = False
        else:
            self.IP_address = 'IP: ___.___.___.___'

        if self.temp_CPU:
            self.cpu_temp_label = Label(
                self.middleframe_inside,
                text='CPU 21 °C',
                fg='lightblue',
                bg='black',
                font=("SFUIText", self.font_size, "bold")
            )
            if self.anchor == 'nw':
                self.cpu_temp_label.pack(side=LEFT)
            else:
                self.cpu_temp_label.pack(side=RIGHT)

        if self.temp_GPU:
            self.gpu_temp_label = Label(
                self.topframe_inside,
                text='GPU 22 °C',
                fg='lightblue',
                bg='black',
                font=("SFUIText", self.font_size, "bold")
            )
            if self.anchor == 'nw':
                self.gpu_temp_label.pack(side=LEFT)
            else:
                self.gpu_temp_label.pack(side=RIGHT)

        if self.IP_address:
            self.ip_address_label = Label(
                self.bottomframe_inside,
                text='000.000.000.000',
                fg='lightblue',
                bg='black',
                font=("SFUIText", self.font_size, "bold")
            )
            if self.anchor == 'nw':
                self.ip_address_label.pack(side=LEFT)
            else:
                self.ip_address_label.pack(side=RIGHT)

        self.window.update_idletasks()
        self.get_font_size()

        self.logger.info('Statusbar widget has been created.')
        self.show = True
        self.status()

    def get_font_size(self):
        """ The method decreases the font size until it satisfies the target
            width and height of the widget."""
        while self.font_size > 12:
            if self.temp_CPU:
                self.cpu_temp_label.config(font=("SFUIText", self.font_size, "bold"))
            if self.temp_GPU:
                self.gpu_temp_label.config(font=("SFUIText", self.font_size, "bold"))
            if self.IP_address:
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
        if self.temp_CPU:
            self.cpu_temp_label.config(text=self.temp_CPU)
        if self.temp_GPU:
            self.gpu_temp_label.config(text=self.temp_GPU)
        if self.IP_address:
            self.ip_address_label.config(text=self.IP_address)
        self.measure_temp()

    def measure_temp(self):
        if self.temp_CPU:
            try:
                self.temp_CPU = subprocess.Popen(
                    'cat /sys/class/thermal/thermal_zone0/temp',
                    shell=True, 
                    stdin=None, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE
                )

                self.temp_CPU, _ = self.temp_CPU.communicate() 
                self.temp_CPU = round(int(self.temp_CPU.decode('utf-8')) / 1000, 1)
                self.temp_CPU = f'CPU {str(self.temp_CPU)}°C'
            except Exception as exc:
                self.temp_CPU = ''
                self.logger.error(f'Cannot get the CPU temp: {exc}')

        if self.temp_GPU:
            try:
                self.temp_GPU = subprocess.Popen(
                    'vcgencmd measure_temp',
                    shell=True, 
                    stdin=None, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE
                )
                self.temp_GPU, _ = self.temp_GPU.communicate()
                self.temp_GPU = self.temp_GPU.decode('utf-8')
                self.temp_GPU = self.temp_GPU[self.temp_GPU.find('=') + 1: self.temp_GPU.find("'")]
                self.temp_GPU = float(self.temp_GPU)
                self.temp_GPU = f'GPU {self.temp_GPU}°C'
            except Exception as exc:
                self.logger.error(f'Cannot get the GPU temp: {exc}')

        if self.IP_address:
            try:
                self.IP_address = subprocess.Popen(
                    'hostname -I',
                    shell=True, 
                    stdin=None, 
                    stdout=subprocess.PIPE, 
                    stderr=subprocess.PIPE
                )

                self.IP_address, _ = self.IP_address.communicate()
                self.IP_address = f'IP: {self.IP_address.decode("utf-8")}'
            except Exception as exc:
                self.logger.error(f'Cannot get the IP address: {exc}')

        self.statusbar_frame.after(self.REFRESH_RATE, self.status)

    def widget_update(self, *args):
        try:
            self.logger.debug('Updating statusbar widget...')
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

            self.statusbar_frame.place(
                relx=self.relx,
                rely=self.rely,
                anchor=self.anchor
            )
            if self.cpu_temp_label:
                self.cpu_temp_label.config(text='CPU __._°C')
            if self.gpu_temp_label:
                self.gpu_temp_label.config(text='GPU __._°C')
            if self.ip_address_label:
                self.ip_address_label.config(text='000.000.000.000')

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
                sticky=self.anchor
            )

            if self.anchor == 'nw':
                if self.temp_CPU:
                    self.cpu_temp_label.pack(side=LEFT)
                if self.temp_GPU:
                    self.gpu_temp_label.pack(side = LEFT)
                if self.IP_address:
                    self.ip_address_label.pack(side = LEFT)
            else:
                if self.temp_CPU:
                    self.cpu_temp_label.pack(side=RIGHT)
                if self.temp_GPU:
                    self.gpu_temp_label.pack(side = RIGHT)
                if self.IP_address:
                    self.ip_address_label.pack(side = RIGHT)
            self.logger.debug('Widget has been updated!')
        except Exception as exc:
            self.logger.error(f'Cannot update the widget: {exc}')

    def destroy(self):
        self.logger.debug('Closing Statusbar...')
        self.statusbar_frame.destroy()

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