#!/usr/bin/python3
# voice_assistant_widget.py - a widget that displays a moving sound wave gif and a text message.
# To display a message put a desired string into self.message.
# The message is displayed for the number of milliseconds set in self.default_timeout variable.
# To display the wave set self.show_wave = True and execute self.show_wave_widget method.

import logging
import os
from tkinter import *
from PIL import Image, ImageTk, ImageSequence

class VoiceAssistantWidget:

    def __init__(
        self,
        window,
        relx=0.2, 
        rely=0.4, 
        width=0.1, 
        height=0.1, 
        anchor='nw',
        show=True        
    ):

        self.logger = logging.getLogger('SM.voice_assistant_widget')
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
        self.show = show

        self.font_size = 30

        self.default_timeout = 4000 #default number of milliseconds to display message.
        self.timeout = self.default_timeout

        self.assistant_frame = Frame(self.window, bg='black', bd=2)
        self.assistant_frame.place(relx=self.relx, rely=self.rely)

        #self.icon_wave_file = Image.open(f'{os.path.dirname(os.path.realpath(__file__))}{os.sep}icons{os.sep}biohazard.png')
        self.frames = [PhotoImage(file=f'{os.path.dirname(os.path.realpath(__file__))}{os.sep}images{os.sep}wave.gif',format = 'gif -index %i' %(i)) for i in range(1,40)]

        self.icon_wave_file = Image.open(f'{os.path.dirname(os.path.realpath(__file__))}{os.sep}images{os.sep}wave.gif')

        self.wave_label = Label(self.assistant_frame, image=self.frames[0], bg='black', bd=0)
        self.wave_label.grid(column=0, row=0, sticky='nw')

        self.message = 'ОШИБКА: РЕЧЬ НЕ РАСПОЗНАНА'
        self.message_label = Message(
            self.assistant_frame, 
            aspect=150,
            padx=5,
            pady=5,
            text=self.message, 
            #width=self.message_label_target_width,
            fg='lightblue', bg='black', 
            font=("SFUIText", self.font_size, "bold")
        )
        self.message_label.grid(column=1, row=0, sticky=self.anchor)

        self.show_wave = False
        self.get_font_size()
        self.logger.info('Voice assistant widget has been initialized!')
        self.status()

    def get_font_size(self):
        """ The method decreases the font size until it satisfies the target
            width and height of the widget."""
        while self.font_size > 8:
            self.message_label.config(font=("SFUIText", self.font_size, "bold"))
            
            icon_wave_file_resized = self.icon_wave_file.resize((int(self.font_size * 16), int(self.font_size * 10)), Image.ANTIALIAS)
            self.icon_wave = ImageTk.PhotoImage(icon_wave_file_resized)
            self.wave_label.config(image=self.icon_wave)

            self.window.update()
            self.message_label_width = self.message_label.winfo_width()
            self.message_label_height = self.message_label.winfo_height()
            if self.message_label_width > self.target_width or self.message_label_height > self.target_height:
                self.font_size -= 1
            else:
                #self.logger.debug(f'Target widget width {self.target_width}')
                #self.logger.debug(f'Real widget width {int(self.message_label_width)}')
                #self.logger.debug(f'Target widget height {self.target_height}')
                #self.logger.debug(f'Real widget height {int(self.message_label_height)}')
                

                zoom_factor = self.font_size * 16 / self.frames[0].width()
                if zoom_factor > 2:
                    for i in range(len(self.frames)):
                        self.frames[i] = self.frames[i].zoom(int(zoom_factor))
                break
        self.message = ''
        self.wave_label.config(image='')

    def status(self):
        if self.show:
            self.assistant_frame.place(
                relx=self.relx, 
                rely=self.rely, 
                anchor=self.anchor
            )
            if self.message != '':
                self.timeout -= 1000
                if self.timeout <= 0:
                    self.timeout = self.default_timeout
                    self.message = ''
            self.message_label.config(text=self.message)
        else:
            self.assistant_frame.place_forget()
        self.assistant_frame.after(1000, self.status)

    def show_wave_widget(self, ind=0):
        try:
            if self.show and self.show_wave:
                frame = self.frames[ind]

                ind += 1
                if ind == len(self.frames) - 1:
                    ind = 0
                self.wave_label.configure(image=frame)
                
                self.wave_label.after(100, self.show_wave_widget, ind)
            else:
                self.wave_label.configure(image='')
        except Exception as exc:
            self.logger.warning(f'Cannot display widget: {exc}')

    def widget_update(self, *args):
        try:
            self.logger.debug('Updating Voice Assistant widget...')
            self.relx = args[0]
            self.rely = args[1]
            width = args[2]
            height = args[3]
            self.anchor = args[4]
            self.target_width = int(width * self.window_width)
            self.target_height = int(height * self.window_height)

            self.assistant_frame.place(
                relx=self.relx, 
                rely=self.rely, 
                anchor=self.anchor
            )

            self.message_label.config(text='ОШИБКА: РЕЧЬ НЕ РАСПОЗНАНА')

            self.get_font_size()            
            self.logger.debug('Widget has been updated!')
        except Exception as exc:
            self.logger.error(f'Cannot update the widget: {exc}')

    def destroy(self):
        self.logger.debug('Closing Voice Assistant...')
        self.assistant_frame.destroy()

if __name__ == '__main__':
    window = Tk()
    window.title('Main Window')
    window.configure(bg='black')
    #window.overrideredirect(True)
    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    window.geometry("%dx%d+0+0" % (w, h))
    widget = VoiceAssistantWidget(window)

    widget.show_wave = True
    widget.show_wave_widget()
    window.mainloop()

__version__ = '0.97' # 19th November 2020
__author__ = 'Dmitry Kudryashov'
__maintainer__ = 'Dmitry Kudryashov'
__email__ = "dmitry-kud@yandex.ru"
__status__ = "Development"