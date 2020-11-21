#!/usr/bin/python3
# calendar2.py - creates a calendar widgets and updates the current date.
# Cannot name the module calendar.py because there is a confilct in modules'
# names when importing requests.

from tkinter import *
import datetime
import time
import logging

class Calendar:

    def __init__(self, window, relx=0.05, rely=0.15, width=0.36, height=0.12, anchor='nw', show=True):

        self.logger = logging.getLogger('SM.calendar')
        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)
            
        # Dimesnsions of the main window (screen size)
        self.window_width = window.winfo_screenwidth()
        self.window_height = window.winfo_screenheight()

        self.relx = relx
        self.anchor = anchor
        self.rely = rely
        self.target_width = int(width * self.window_width)
        self.target_height = int(height * self.window_height)
        self.show = show

        # Initial font size
        self.font_size = 28

        self.date_label = Label(
            window, text='Понедельник, 00 сентября', 
            fg='lightblue', 
            bg='black', 
            font=("SFUIText", self.font_size, "bold")
        )

        if self.anchor == 'e':
            self.relx += width

        self.date_label.place(relx=self.relx, rely=self.rely, anchor=self.anchor)

        self.date_label.update()
        self.date_label_width = self.date_label.winfo_width()
        self.date_label_height = self.date_label.winfo_height()

        self.get_font_size()

        self.months = {1: 'января', 2: 'февраля', 3: 'марта', 4: 'апреля', 5: 'мая', 6: 'июня',
                       7: 'июля', 8: 'августа', 9: 'сентября', 10: 'октября', 11: 'ноября', 12: 'декабря'}
        self.weekdays = {0: 'Понедельник', 1: 'Вторник', 2: 'Среда', 3: 'Четверг', 4: 'Пятница', 5: 'Суббота', 6: 'Воскресенье'}

        self.current_date_and_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)

        self.logger.info('Calendar widget has been created.')

        self.widget()

    def get_font_size(self):
        """ The method decreases the font size until it satisfies the target
            width and height of the widget."""
        while self.font_size > 12:
            self.date_label.config(font=("SFUIText", self.font_size, "bold"))
            self.date_label.update()
            self.date_label_width = self.date_label.winfo_width()
            self.date_label_height = self.date_label.winfo_height()
            if self.date_label_width > self.target_width or self.date_label_height > self.target_height:
                self.font_size -= 1
            else:
                #self.logger.debug(f'Target widget width {self.target_width}')
                #self.logger.debug(f'Real widget width {int(self.date_label_width)}')
                #self.logger.debug(f'Target widget height {self.target_height}')
                #self.logger.debug(f'Real widget height {int(self.date_label_height)}')
                break

    def get_time(self):
        """ Determines the current date and time, returns the datetime object as well as 
            the current time as a string in the format HH:MM:SS."""
        self.current_date_and_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
        return self.current_date_and_time

    def widget(self):
        """ Gets the current date and time object. If the day date is less than 10 adds a leading zero
            in order to maintain the same string date length. 
            Assigns to dateLbl the current date in the format {weekday}, DD {month}."""
        current_date_and_time = self.get_time()

        days = current_date_and_time.day
        days = str(days)
        # Translates the weekday as a digit into the name of the weekday.
        weekday = self.weekdays[current_date_and_time.weekday()]
        # Translates the month number into the name of the month.
        month = self.months[current_date_and_time.month]
        self.current_date_str =  f'{weekday}, {days} {month}'
        self.date_label.config(text=self.current_date_str)

        self.date_label.after(1000, self.status)

    def status(self):
        if self.show:
            self.date_label.place(relx=self.relx, rely=self.rely, anchor=self.anchor)
            self.widget()
        else:
            self.date_label.place_forget()
            self.date_label.after(1000, self.status)

    def widget_update(self, *args):
        try:
            self.logger.debug('Updating Calendar widget...')
            self.relx = args[0]
            self.rely = args[1]
            width = args[2]
            height = args[3]
            self.anchor = args[4]
            if self.anchor == 'e':
                self.relx += width
            self.target_width = int(width * self.window_width)
            self.target_height = int(height * self.window_height)
            self.font_size = 28

            self.date_label.place(relx=self.relx, rely=self.rely, anchor=self.anchor)
            self.date_label.config(text='Понедельник, 00 сентября')
            
            self.get_font_size()
            self.logger.debug('Widget has been updated!')
        except Exception as exc:
            self.logger.error(f'Cannot update the widget: {exc}')

    def destroy(self):
        self.logger.debug('Closing Calendar...')
        self.date_label.destroy()

if __name__ == '__main__':
    try:
        window = Tk()
        window.title('Main Window')
        window.configure(bg='black')
        #window.overrideredirect(True)
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry("%dx%d+0+0" % (w, h))
        a = Calendar(window)
        window.mainloop()
    except KeyboardInterrupt:
        sys.exit()

__version__ = '0.97' # 19th November 2020
__author__ = 'Dmitry Kudryashov'
__maintainer__ = 'Dmitry Kudryashov'
__email__ = "dmitry-kud@yandex.ru"    
__status__ = "Development"