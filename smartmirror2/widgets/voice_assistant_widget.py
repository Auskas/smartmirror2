#!/usr/bin/python3
# voice_assistant_widget.py

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
        anchor='nw'        
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

        self.font_size = 30

        self.assistant_frame = Frame(self.window, bg='black', bd=2)
        self.assistant_frame.place(relx=self.relx, rely=self.rely)

        #self.icon_wave_file = Image.open(f'{os.path.dirname(os.path.realpath(__file__))}{os.sep}icons{os.sep}biohazard.png')
        self.frames = [PhotoImage(file=f'{os.path.dirname(os.path.realpath(__file__))}{os.sep}images{os.sep}wave.gif',format = 'gif -index %i' %(i)) for i in range(1,40)]

        self.icon_wave_file = Image.open(f'{os.path.dirname(os.path.realpath(__file__))}{os.sep}images{os.sep}wave.gif')

        self.wave_label = Label(self.assistant_frame, image=self.frames[0], bg='black', bd=0)
        self.wave_label.grid(column=0, row=0, sticky='nw')

        self.test_message = 'In the town where I was born lived a man who sailed to sea'
        #self.message_label_target_width = self.target_width - self.frames[0].width()

        self.message = 'ГОВОРИТЕ: '
        self.message_label = Message(
            self.assistant_frame, 
            aspect=150,
            padx=5,
            pady=5,
            text=self.test_message, 
            #width=self.message_label_target_width,
            fg='lightblue', bg='black', 
            font=("SFUIText", self.font_size, "bold")
        )
        self.message_label.grid(column=1, row=0, sticky=self.anchor)

        self.show = True
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
            self.time_label_width = self.message_label.winfo_width()
            self.time_label_height = self.message_label.winfo_height()
            if self.time_label_width > self.target_width or self.time_label_height > self.target_height:
                self.font_size -= 1
            else:
                self.logger.debug(f'Target widget width {self.target_width}')
                self.logger.debug(f'Real widget width {int(self.time_label_width)}')
                self.logger.debug(f'Target widget height {self.target_height}')
                self.logger.debug(f'Real widget height {int(self.time_label_height)}')
                

                zoom_factor = self.font_size * 16 / self.frames[0].width()
                if zoom_factor > 2:
                    for i in range(len(self.frames)):
                        self.frames[i] = self.frames[i].zoom(int(zoom_factor))
                break
        self.message_label.config(text='')
        self.wave_label.config(image='')

    def status(self):
        if self.show:
            self.assistant_frame.place(
                relx=self.relx, 
                rely=self.rely, 
                anchor=self.anchor
            )
        else:
            self.assistant_frame.place_forget()
        self.assistant_frame.after(1000, self.status)

    def show_wave_widget(self, ind=0):
        try:
            if self.show and self.show_wave:
                #self.message_label.config(text=self.message)
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
        self.relx = args[0]
        self.rely = args[1]
        width = args[2]
        height = args[3]
        self.anchor = args[4]
        self.target_width = int(width * self.window_width)
        self.target_height = int(height * self.window_height)

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