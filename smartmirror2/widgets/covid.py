#!/usr/bin/python3
# covid.py - a widget that displays the current Covid-19 cases.

from tkinter import *
import logging
from PIL import Image, ImageTk
import os

class Covid:

    def __init__(self, window, relx=0.62, rely=0.03, width=0.36, height=0.09, anchor='nw'):
        self.logger = logging.getLogger('SM.covid')
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

        # The initial size of the widget fonts. It is resized to occupy the target dimesions.
        self.font_size = 30

        # Loading biohazard, scull, and heart icons.
        self.icon_cases_file = Image.open(f'{os.path.dirname(os.path.realpath(__file__))}{os.sep}icons{os.sep}biohazard.png')
        self.icon_deaths_file = Image.open(f'{os.path.dirname(os.path.realpath(__file__))}{os.sep}icons{os.sep}scull.png')
        self.icon_recovered_file = Image.open(f'{os.path.dirname(os.path.realpath(__file__))}{os.sep}icons{os.sep}heart.png')

        # Main frame for the widget.
        self.covid_frame = Frame(window, bg='black', bd=0)
        self.covid_frame.place(relx=self.relx, rely=self.rely)

        # The inner top frame with the world Covid-19 cases.
        self.top_frame = Frame(self.covid_frame, bg='black', bd=0)
        self.top_frame.grid(column=0, row=0, sticky=self.anchor)

        # The leftmost frame inside the top frame to display the total number of cases.
        self.top_frame_cases = Frame(self.top_frame, bg='black', bd=0)
        self.top_frame_cases.grid(column=0, row=0, sticky=self.anchor)

        icon_cases_file_resized = self.icon_cases_file.resize((int(self.font_size * 1.9), int(self.font_size * 1.9)), Image.ANTIALIAS)
        self.render_cases_world = ImageTk.PhotoImage(icon_cases_file_resized)
        self.icon_cases_world = Label(self.top_frame_cases, image=self.render_cases_world, bg='black')
        self.icon_cases_world.grid(column=0, row=0, sticky=self.anchor)

        # The middle frame inside the top frame to display the number of deaths.
        self.world_cases = Label(self.top_frame_cases, text='000,000,000', fg='white', bg='black', font=("SFUIText", self.font_size, "bold"))
        self.world_cases.grid(column=1, row=0, sticky=self.anchor)

        self.top_frame_deaths = Frame(self.top_frame, bg='black', bd=0)
        self.top_frame_deaths.grid(column=1, row=0, sticky=self.anchor)

        # Loads and places the scull icon.

        icon_deaths_file_resized = self.icon_deaths_file.resize((int(self.font_size * 1.9), int(self.font_size * 1.9)), Image.ANTIALIAS)
        self.render_deaths = ImageTk.PhotoImage(icon_deaths_file_resized)
        self.icon_deaths_world = Label(self.top_frame_deaths, image=self.render_deaths, bg='black')
        self.icon_deaths_world.grid(column=0, row=0, sticky=self.anchor)

        # The rightmost frame inside the top frame to display the number of recovered.
        self.world_deaths = Label(self.top_frame_deaths, text='000,000,000', fg='white', bg='black', font=("SFUIText", self.font_size, "bold"))
        self.world_deaths.grid(column=1, row=0, sticky=self.anchor)

        self.top_frame_recovered = Frame(self.top_frame, bg='black', bd=0)
        self.top_frame_recovered.grid(column=2, row=0, sticky=self.anchor)

        # Loads and places the heart icon.

        icon_recovered_file_resized = self.icon_recovered_file.resize((int(self.font_size * 1.9), int(self.font_size * 1.9)), Image.ANTIALIAS)
        self.render_recovered = ImageTk.PhotoImage(icon_recovered_file_resized)
        self.icon_recovered_world = Label(self.top_frame_recovered, image=self.render_recovered, bg='black')
        self.icon_recovered_world.grid(column=0, row=0, sticky=self.anchor)
        self.world_recovered = Label(self.top_frame_recovered, text='000,000,000', fg='white', bg='black', font=("SFUIText", self.font_size, "bold"))
        self.world_recovered.grid(column=1, row=0, sticky=self.anchor)

        # The inner bottom frame with russian Covid-19 cases.
        self.bottom_frame = Frame(self.covid_frame, bg='black', bd=0)
        self.bottom_frame.grid(column=0, row=1, sticky=self.anchor)

        # The leftmost frame inside the top frame to display the number of cases in Russia.
        self.bottom_frame_cases = Frame(self.bottom_frame, bg='black', bd=0)
        self.bottom_frame_cases.grid(column=0, row=0, sticky=self.anchor)

        # Loads and places the biohazard icon for the bottom frame.
        self.RUS = Label(self.bottom_frame_cases, text='RUS ', fg='white', bg='black', font=("SFUIText", self.font_size - 2, "bold"))
        self.RUS.grid(column=0, row=0, sticky=self.anchor)

        icon_cases_rus_file_resized = self.icon_cases_file.resize((int(self.font_size * 1.5), int(self.font_size * 1.5)), Image.ANTIALIAS)
        self.render_cases_rus = ImageTk.PhotoImage(icon_cases_rus_file_resized)
        self.icon_cases_rus = Label(self.bottom_frame_cases, image=self.render_cases_rus, bg='black')
        self.icon_cases_rus.grid(column=1, row=0, sticky=self.anchor)

        self.rus_cases = Label(self.bottom_frame_cases, text='00,000,000 (+00,000)', fg='white', bg='black', font=("SFUIText", self.font_size - 2, "bold"))
        self.rus_cases.grid(column=2, row=0, sticky='w')

        # Loads and places the scull icon for the bottom frame.
        icon_deaths_rus_file_resized = self.icon_deaths_file.resize((int(self.font_size * 1.5), int(self.font_size * 1.5)), Image.ANTIALIAS)
        self.render_deaths_rus = ImageTk.PhotoImage(icon_deaths_rus_file_resized)
        self.icon_deaths_rus = Label(self.bottom_frame_cases, image=self.render_deaths_rus, bg='black')
        self.icon_deaths_rus.grid(column=3, row=0, sticky=self.anchor)

        self.rus_deaths = Label(self.bottom_frame_cases, text='000,000 (+0,000)', fg='white', bg='black', font=("SFUIText", self.font_size - 2, "bold"))
        self.rus_deaths.grid(column=4, row=0, sticky=self.anchor)

        # Loads and places the heart icon for the bottom frame.
        icon_recovered_rus_file_resized = self.icon_recovered_file.resize((int(self.font_size * 1.5), int(self.font_size * 1.5)), Image.ANTIALIAS)
        self.render_recovered_rus = ImageTk.PhotoImage(icon_recovered_rus_file_resized)
        self.icon_recovered_rus = Label(self.bottom_frame_cases, image=self.render_recovered_rus, bg='black')
        self.icon_recovered_rus.grid(column=5, row=0, sticky=self.anchor)

        self.rus_recovered = Label(self.bottom_frame_cases, text='00,000,000', fg='white', bg='black', font=("SFUIText", self.font_size - 2, "bold"))
        self.rus_recovered.grid(column=6, row=0, sticky=self.anchor)

        self.show = True

        # Default Covid-19 data
        self.covid_figures = [
            '24,925,950', '861,668', '18,209,780',
            '1,000,500', '+4,952',
            '17,414', '+31',
            '821,169'
        ]
        self.covid_test_figures = [
            '24,925,950', '861,668', '18,209,780',
            '1,000,500', '+4,952',
            '17,414', '+31',
            '821,169'
        ]

        self.covid_frame.update()
        self.covid_frame_width = self.covid_frame.winfo_width()
        self.covid_frame_height = self.covid_frame.winfo_height()
        #print(int(self.covid_frame_width / self.window_width * 100))
        #print(int(self.covid_frame_height / self.window_height * 100))
        self.get_font_size()
        self.logger.info('Covid widget has been created.')
        self.widget()

    def get_font_size(self):
        """ The method decreases the font size until it satisfies the target
            width and height of the widget."""
        while self.font_size > 12:

            self.world_cases.config(font=("SFUIText", self.font_size, "bold"))
            self.world_deaths.config(font=("SFUIText", self.font_size, "bold"))
            self.world_recovered.config(font=("SFUIText", self.font_size, "bold"))
            self.RUS.config(font=("SFUIText", self.font_size - 2, "bold"))
            self.rus_cases.config(font=("SFUIText", self.font_size - 2, "bold"))
            self.rus_deaths.config(font=("SFUIText", self.font_size - 2, "bold"))
            self.rus_recovered.config(font=("SFUIText", self.font_size - 2, "bold"))

            icon_cases_file_resized = self.icon_cases_file.resize((int(self.font_size * 1.9), int(self.font_size * 1.9)), Image.ANTIALIAS)
            self.render_cases_world = ImageTk.PhotoImage(icon_cases_file_resized)
            self.icon_cases_world.config(image=self.render_cases_world)

            icon_cases_file_resized = self.icon_cases_file.resize((int(self.font_size * 1.5), int(self.font_size * 1.5)), Image.ANTIALIAS)
            self.render_cases_rus = ImageTk.PhotoImage(icon_cases_file_resized)
            self.icon_cases_rus.config(image=self.render_cases_rus)

            icon_deaths_file_resized = self.icon_deaths_file.resize((int(self.font_size * 1.9), int(self.font_size * 1.9)), Image.ANTIALIAS)
            self.render_deaths_world = ImageTk.PhotoImage(icon_deaths_file_resized)
            self.icon_deaths_world.config(image=self.render_deaths_world)

            icon_deaths_file_resized = self.icon_deaths_file.resize((int(self.font_size * 1.5), int(self.font_size * 1.5)), Image.ANTIALIAS)
            self.render_deaths_rus = ImageTk.PhotoImage(icon_deaths_file_resized)
            self.icon_deaths_rus.config(image=self.render_deaths_rus)

            icon_recovered_file_resized = self.icon_recovered_file.resize((int(self.font_size * 1.9), int(self.font_size * 1.9)), Image.ANTIALIAS)
            self.render_recovered_world = ImageTk.PhotoImage(icon_recovered_file_resized)
            self.icon_recovered_world.config(image=self.render_recovered_world)

            icon_recovered_file_resized = self.icon_recovered_file.resize((int(self.font_size * 1.5), int(self.font_size * 1.5)), Image.ANTIALIAS)
            self.render_recovered_rus = ImageTk.PhotoImage(icon_recovered_file_resized)
            self.icon_recovered_rus.config(image=self.render_recovered_rus)

            self.window.update()

            self.covid_frame_width = self.covid_frame.winfo_width()
            self.covid_frame_height = self.covid_frame.winfo_height()

            if self.covid_frame_width > self.target_width or self.covid_frame_height > self.target_height:
                self.font_size -= 1
            else:
                self.logger.debug(f'Target widget width {self.target_width}')
                self.logger.debug(f'Real widget width {int(self.covid_frame_width)}')
                self.logger.debug(f'Target widget height {self.target_height}')
                self.logger.debug(f'Real widget height {int(self.covid_frame_height)}')
                break

    def widget(self):
        self.world_cases.config(text=f'{self.covid_figures[0]} ')
        self.world_deaths.config(text=f'{self.covid_figures[1]} ')
        self.world_recovered.config(text=self.covid_figures[2])
        self.rus_cases.config(text=f'{self.covid_figures[3]} ({self.covid_figures[4]})  ')
        self.rus_deaths.config(text=f'{self.covid_figures[5]} ({self.covid_figures[6]})  ')
        self.rus_recovered.config(text=self.covid_figures[7])

        #self.icon_cases_world.config(image=self.render_cases_world)
        #self.icon_deaths_world.configure(image=self.render_deaths)
        #self.icon_recovered_world.configure(image=self.render_recovered)
        #self.icon_cases_rus.configure(image=self.render_cases_rus)
        #self.icon_deaths_rus.configure(image=self.render_deaths_rus)
        #self.icon_recovered_rus.configure(image=self.render_recovered_rus)

        self.world_cases.after(1000, self.status)

    def status(self):
        if self.show:
            self.covid_frame.place(relx=self.relx, rely=self.rely)
            self.widget()
        else:
            self.covid_frame.place_forget()
            self.covid_frame.after(1000, self.status)

    def widget_update(self, *args):
        try:
            self.logger.debug('Updating Covid-19 widget...')
            self.relx = args[0]
            self.rely = args[1]
            width = args[2]
            height = args[3]
            self.anchor = args[4]
            self.target_width = int(width * self.window_width)
            self.target_height = int(height * self.window_height)
            self.font_size = 40

            self.covid_frame.place(relx=self.relx, rely=self.rely)

            self.get_font_size()
            self.logger.debug('Widget has been updated!')
        except Exception as exc:
            self.logger.error(f'Cannot update the widget: {exc}')

    def destroy(self):
        self.logger.debug('Closing Covid-19...')
        self.covid_frame.destroy()
            
if __name__ == '__main__':
    try:
        window = Tk()
        window.title('Main Window')
        window.configure(bg='black')
        #window.overrideredirect(True)
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry("%dx%d+0+0" % (w, h))
        a = Covid(window)
        window.mainloop()
    except KeyboardInterrupt:
        sys.exit()

__version__ = '0.96' # 10th September 2020
__author__ = 'Dmitry Kudryashov'
__maintainer__ = 'Dmitry Kudryashov'
__email__ = "dmitry-kud@yandex.ru"
__status__ = "Development"