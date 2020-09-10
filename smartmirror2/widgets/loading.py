#!/usr/bin/python3
# loading.py - a widget that displays the loading state.

from tkinter import *
import logging
from PIL import Image, ImageTk
import os

class Loading:

    def __init__(self, window):
        self.logger = logging.getLogger('SM.loading')
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

        self.frames = [PhotoImage(
            file=f'.{os.sep}images{os.sep}loading{os.sep}{i}.png',
            ) for i in range(0,8)
        ]
        for i in range(len(self.frames)):
            self.frames[i] = self.frames[i].subsample(2,2)
        self.backup_image = PhotoImage(
            file=f'.{os.sep}images{os.sep}loading.png'
        )
        print(f'Number of gif frames {len(self.frames)}')
        self.loading_label = Label(
            self.window, 
            bg='black', 
            bd=0,
            width=self.window_width, 
            height=self.window_height,
        )
        self.loading_label.pack()
        #self.loading_label.configure(image=self.backup_image)
        self.logger.info('Loading widget has been created.')
        self.widget()

    def widget(self, ind=0):
        frame = self.frames[ind]
        self.loading_label.configure(image=frame)
        ind += 1
        if ind == len(self.frames):
            self.loading_label.after(120, self.widget, 0)
        else:
            self.loading_label.after(120, self.widget, ind)

if __name__ == '__main__':
    try:
        window = Tk()
        window.title('Main Window')
        window.configure(bg='black')
        #window.overrideredirect(True)
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry("%dx%d+0+0" % (w, h))
        a = Loading(window)
        window.mainloop()
    except KeyboardInterrupt:
        sys.exit()