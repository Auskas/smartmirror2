#!/usr/bin/python3
# stocks.py - creates a stocks widget to display the exchange rates.

from tkinter import *
import datetime
import time
import logging

class Stocks:

    def __init__(self, window, relx=0.65, rely=0.65, width=0.4, height=0.1, anchor='ne'):
        self.logger = logging.getLogger('SM.stocks')

        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)

        self.font_size = 40

        # Dimesnsions of the main window (screen size)
        self.window_width = window.winfo_screenwidth()
        self.window_height = window.winfo_screenheight()

        self.relx = relx
        self.rely = rely
        self.target_width = int(width * self.window_width)
        self.target_height = int(height * self.window_height)

        self.anchor = anchor

        self.rates_string = '*** Обновление данных по котировкам ***'
        self.rates_test_string = '$ 000.0↓   € 000.0↓   Brent 000.0↑'
        self.stocks_label = Label(
            window, text=self.rates_test_string, 
            fg='lightblue', bg='black', 
            font=("SFUIText", self.font_size, "bold")
        )
        if self.anchor == 'ne':
            self.relx += width
        self.stocks_label.place(relx=self.relx, rely=self.rely, anchor=self.anchor)
        
        self.show = True
        
        self.get_font_size()

        self.logger.debug('Stocks Widget has been created.')
        self.widget()

    def get_font_size(self):
        while self.font_size > 12:
            self.stocks_label.config(font=("SFUIText", self.font_size, "bold"))
            self.stocks_label.update()
            self.stocks_label_width = self.stocks_label.winfo_width()
            self.stocks_label_height = self.stocks_label.winfo_height()
            if self.stocks_label_width > self.target_width or self.stocks_label_height > self.target_height:
                if self.stocks_label_width > self.target_width * 3 or self.stocks_label_height > self.target_height * 3:
                    self.font_size -= 5
                elif self.stocks_label_width > self.target_width * 2 or self.stocks_label_height > self.target_height * 2:
                    self.font_size -= 3
                else:
                    self.font_size -= 1
            else:
                self.logger.debug(f'Target widget width {self.target_width}')
                self.logger.debug(f'Real widget width {int(self.stocks_label_width)}')
                self.logger.debug(f'Target widget height {self.target_height}')
                self.logger.debug(f'Real widget height {int(self.stocks_label_height)}')
                self.stocks_label.config(text='*** Обновление данных по котировкам ***')
                break
        self.stocks_label.config(text='*** Обновление данных по котировкам ***')

    def widget(self):
        self.stocks_label.after(1000, self.status)
        self.stocks_label.configure(text=self.rates_string)
        
    def status(self):
        if self.show:
            self.stocks_label.place(
                relx=self.relx, 
                rely=self.rely,
                anchor=self.anchor
            )
            self.widget()
        else:
            self.stocks_label.place_forget()
            self.stocks_label.after(1000, self.status)

    def widget_update(self, *args):
        try:
            self.logger.debug('Updating Stocks widget...')
            self.relx = args[0]
            self.rely = args[1]
            width = args[2]
            height = args[3]
            self.anchor = args[4]
            if self.anchor == 'ne':
                self.relx += width
            self.target_width = int(width * self.window_width)
            self.target_height = int(height * self.window_height)
            self.font_size = 50

            self.stocks_label.place(
                relx=self.relx, 
                rely=self.rely,
                anchor=self.anchor
            )
            self.stocks_label.config(text='$ 000.0↓   € 000.0↓   Brent 000.0↑')

            self.get_font_size()
            self.stocks_label.place(
                relx=self.relx, 
                rely=self.rely,
                anchor=self.anchor
            )
            self.logger.debug('Widget has been updated!')
        except Exception as exc:
            self.logger.error(f'Cannot update the widget: {exc}')

    def destroy(self):
        self.logger.debug('Closing Stocks...')
        self.stocks_label.destroy()

if __name__ == '__main__':
    try:
        window = Tk()
        window.title('Main Window')
        window.configure(bg='black')
        #window.overrideredirect(True)
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry("%dx%d+0+0" % (w, h))
        a = Stocks(window)
        window.mainloop()
    except KeyboardInterrupt:
        sys.exit()