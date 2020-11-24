#!/usr/bin/python3
# clock.py - creates a clock widgets and updates the current time.

from tkinter import *
import datetime
import time
import logging

class Clock:

    def __init__(self, window, relx=0.05, rely=0.05, width=0.2, height=0.1, anchor='nw', show=True, font_color='lightblue'):
        self.logger = logging.getLogger('SM2.clock')

        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)

        self.logger.info('Initialization of CLOCK widget...')

        # Dimesnsions of the main window (screen size)
        self.window_width = window.winfo_screenwidth()
        self.window_height = window.winfo_screenheight()

        self.relx = relx
        self.rely = rely
        self.target_width = int(width * self.window_width)
        self.target_height = int(height * self.window_height)
        self.anchor = anchor
        self.show = show

        self.font_size = 50
        self.timeLbl = Label(
            window, 
            text='00:00:00', 
            fg='lightblue', 
            bg='black', 
            font=("SFUIText", self.font_size, "bold")
        )
        
        if self.anchor == 'ne':
            self.relx += width

        self.timeLbl.place(relx=self.relx, rely=self.rely, anchor=self.anchor)
        self.timeLbl.update()
        self.time_label_width = self.timeLbl.winfo_width()
        self.time_label_height = self.timeLbl.winfo_height()
        self.get_font_size()

        self.logger.info('CLOCK widgets has been created.')
        self.status()

    def get_font_size(self):
        """ The method decreases the font size until it satisfies the target
            width and height of the widget."""
        while self.font_size > 12:
            self.timeLbl.config(font=("SFUIText", self.font_size, "bold"))
            self.timeLbl.update()
            self.time_label_width = self.timeLbl.winfo_width()
            self.time_label_height = self.timeLbl.winfo_height()
            if self.time_label_width > self.target_width or self.time_label_height > self.target_height:
                if self.time_label_width > self.target_width * 3 or self.time_label_height > self.target_height * 3:
                    self.font_size -= 5
                elif self.time_label_width > self.target_width * 2 or self.time_label_height > self.target_height * 2:
                    self.font_size -= 3
                else:
                    self.font_size -= 1
            else:
                #self.logger.debug(f'Target widget width {self.target_width}')
                #self.logger.debug(f'Real widget width {int(self.time_label_width)}')
                #self.logger.debug(f'Target widget height {self.target_height}')
                #self.logger.debug(f'Real widget height {int(self.time_label_height)}')
                break
        
    def get_time(self):
        """ Determines the current date and time, returns the datetime object as well as 
            the current time as a string in the format HH:MM:SS."""
        self.current_date_and_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        current_time_str = self.current_date_and_time.strftime('%H:%M:%S')
        return current_time_str, self.current_date_and_time

    def widget(self):
        current_time_str, current_date_and_time = self.get_time()
        self.timeLbl.config(text=current_time_str)
        self.timeLbl.after(1000, self.status)
        
    def status(self):
        if self.show:
            self.timeLbl.place(relx=self.relx, rely=self.rely, anchor=self.anchor)
            self.widget()
        else:
            self.timeLbl.place_forget()
            self.timeLbl.after(1000, self.status)

    def widget_update(self, *args):
        try:
            self.logger.debug('Updating Clock widget...')
            self.relx = args[0]
            self.rely = args[1]
            width = args[2]
            height = args[3]
            self.anchor = args[4]
            if self.anchor == 'ne':
                self.relx += width
            self.target_width = int(width * self.window_width)
            self.target_height = int(height * self.window_height)
            self.font_size = 150

            self.timeLbl.place(relx=self.relx, rely=self.rely, anchor=self.anchor)
            self.timeLbl.config(text='00:00:00')
            
            self.get_font_size()
            self.timeLbl.place(relx=self.relx, rely=self.rely, anchor=self.anchor)
            self.logger.debug('Widget has been updated!')
        except Exception as exc:
            self.logger.error(f'Cannot update the widget: {exc}')

    def destroy(self):
        self.logger.debug('Closing Clock...')
        self.timeLbl.destroy()
            
if __name__ == '__main__':
    try:
        window = Tk()
        window.title('Main Window')
        window.configure(bg='black')
        #window.overrideredirect(True)
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry("%dx%d+0+0" % (w, h))
        a = Clock(window)
        window.mainloop()
    except KeyboardInterrupt:
        sys.exit()

__version__ = '0.97' # 19th November 2020
__author__ = 'Dmitry Kudryashov'
__maintainer__ = 'Dmitry Kudryashov'
__email__ = "dmitry-kud@yandex.ru"    
__status__ = "Development"