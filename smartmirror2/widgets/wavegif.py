#!/usr/bin/python3
# wave.py

import logging
from tkinter import *
import os
import sounddevice

class Wavegif:

    def __init__(
        self, 
        window, 
        relx=0.5, 
        rely=0.4, 
        width=0.5, 
        height=0.1, 
        anchor='nw'
    ):
        self.logger = logging.getLogger('SM.wave')

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

        self.frames = [PhotoImage(file=f'images{os.sep}wave.gif',format = 'gif -index %i' %(i)) for i in range(1,40)]
        self.wave_label = Label(self.window, bg='black', bd=0)
        self.wave_label.place(relx=self.relx, rely=self.rely, anchor=self.anchor)

        self.show_widget = False

    def show(self, ind=0):
        try:
            if self.show_widget:
                frame = self.frames[ind]
                ind += 1
                if ind == len(self.frames) - 1:
                    ind = 0
                self.wave_label.configure(image=frame)
                self.wave_label.after(100, self.show, ind)
            else:
                self.wave_label.configure(image='')
        except Exception as exc:
            self.logger.warning(f'Cannot display widget: {exc}')
   
if __name__ == '__main__':
    window = Tk()
    window.title('Main Window')
    window.configure(bg='black')
    #window.overrideredirect(True)
    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    window.geometry("%dx%d+0+0" % (w, h))
    a = Wavegif(window)
    a.show_widget = True
    a.show();
    window.mainloop()
