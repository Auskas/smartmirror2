#!/usr/bin/python3
# ticker.py - a ticker for my Smart Mirror Project.

from tkinter import *
import datetime
import time
import logging

class Ticker():

    def __init__(self, window, relx=0.0, rely=0.93, width=1, height=0.1, anchor='nw', show=True):
        self.st_time = time.perf_counter()

        self.logger = logging.getLogger('SM2.ticker')

        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)

        self.logger.info('Initialization of TICKER widget...')

        # Special news ticker for April's Fool day.
        #self.april_fools_news = 'Владимир Путин выступил на Генеральной ассамблее ООН в костюме Деда Мороза.   ***   Дмитрий Медведев в ходе своего визита на Дальний восток заявил о невозможности разблокировки своего айфона.   ***  Укробандеровские собакофашисты вновь нарушили перемирие на Донбасе, коварно атаковав позиции отважных ополченцев.   ***    В ходе военных учений в Калининградской области российские войска уничтожили двести танков и триста самолетов противника. Условного.   ***   Президент России заявил о двухкратном снижении темпов прироста скорости падения российской экономики.   ***   Согласно опроса ФГЛПРФ ЗД более половины респондентов заявили о беззаговорочной поддержке курса Президента. Кормильца нашего, храни его Бог, благослави все дела его праведные.   ***   Виталий Мутко во время встречи со студентами МГУ признался, что только искренняя любовь к Отчизне заставляет его оставаться на своём посту.   ***   Глава МИД России Сергей Лавров считает овец перед сном.   ***   "Патриотизм и любовь к Родине обязаны быть в сердце каждого россиянина", - заявил Игорь Сечин на встрече с гостями и журналистами на борту своей яхты в Монте-Карло.   ***   Патриарх Московский и Всея Руси Кирилл считает, что российскому обществу следует отказаться от чрезмерной роскоши. В пользу РПЦ.'
        self.april_fools_news2 = [
            'Владимир Путин выступил на Генеральной ассамблее ООН в костюме Деда Мороза.',
            'Дмитрий Медведев в ходе своего визита на Дальний восток заявил о невозможности разблокировки своего айфона.',
            'Укробандеровские собакофашисты вновь нарушили перемирие на Донбасе, коварно атаковав позиции отважных ополченцев.',
            'В ходе военных учений в Калининградской области российские войска уничтожили двести танков и триста самолетов противника. Условного.',
            'Президент России заявил о двухкратном снижении темпов прироста скорости падения российской экономики.',
            'Согласно опроса ФГЛПРФ ЗД более половины респондентов заявили о беззаговорочной поддержке курса Президента. Кормильца нашего, храни его Бог, благослави все дела его праведные.',
            'Виталий Мутко во время встречи со студентами МГУ признался, что только искренняя любовь к Отчизне заставляет его оставаться на своём посту.',
            'Глава МИД России Сергей Лавров считает овец перед сном.',
            '"Патриотизм и любовь к Родине обязаны быть в сердце каждого россиянина", - заявил Игорь Сечин на встрече с гостями и журналистами на борту своей яхты в Монте-Карло.',
            'Патриарх Московский и Всея Руси Кирилл считает, что российскому обществу следует отказаться от чрезмерной роскоши. В пользу РПЦ.'
        ]
        
        self.news_index = 0

        self.test_string = '   *** Загрузка новостей ***   '
        #self.news_list = self.april_fools_news2
        self.news_list = []
        self.font_size = 50

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

        self.TICKER_SPEED = 1
        self.REFRESH_RATE = 15
        
        # borderwidth default size is 2 (we don't need any borders), highlightbackground default is white - when the canvas is not in the focus.
        self.ticker_label = Label(
            self.window,  
            text=self.test_string,
            font=("SFUIText", self.font_size, "bold"),
            borderwidth=0, 
            highlightbackground='black',
            fg = 'lightblue', 
            bg = 'black'
        )

        self.ticker_label.place(x=self.relx, rely=self.rely)
        self.window.update_idletasks()
        
        self.get_font_size()
        #self.window.after(1, self.animate)
        self.logger.debug('TICKER widget has been created.')

    def get_font_size(self):
        """ The method decreases the font size until it satisfies the target
            width and height of the widget."""
        try:
            self.ticker_label.config(font=("SFUIText", self.font_size, "bold"))
            if self.ticker_label.winfo_height() > self.target_height:
                self.font_size -= 1
                if self.font_size == 10:
                    self.ticker_label.config(text=self.test_string)
                    self.ticker_label.place(x=self.window_width, rely=self.rely)
                    self.ticker_label.update()

                    self.logger.debug('Minimum font size has been set (10)')
                    self.ticker_label.after(1, self.animate)
                    
                else:
                    self.ticker_label.after(1, self.get_font_size)
            else:
                self.logger.debug(f'Target widget height {self.target_height}')
                self.logger.debug(f'Real widget height {self.ticker_label.winfo_height()}')
                self.logger.debug(f'The font size is set to {self.font_size}')

                self.ticker_label.config(text=self.test_string)
                self.ticker_label.place(x=self.window_width, rely=self.rely)
                self.ticker_label.update()

                self.window.after(1, self.animate)

            
        except Exception as exc:
            self.logger.error(f'Cannot adjust the size of the widget: {exc}')

    def animate(self):
        if self.show:
            if self.ticker_label.winfo_x() > -self.ticker_label.winfo_width():
                self.ticker_label.place(x=self.ticker_label.winfo_x() - self.TICKER_SPEED, rely=self.rely)
            else:
                #self.logger.info(f'The overall time for one hop is {time.perf_counter() - self.st_time} seconds.')
                number_of_news = len(self.news_list)
                if number_of_news > 0:
                    if self.news_index > number_of_news - 1:
                        self.news_index = 0

                    self.ticker_label.config(text=f'*** {self.news_list[self.news_index]} ***')
                    self.ticker_label.place(x=self.window_width, rely=self.rely)
                    self.ticker_label.update()               

                    self.news_index += 1
                self.ticker_label.place(x=self.window_width, rely=self.rely)
            self.ticker_label.after(self.REFRESH_RATE, self.animate)
        else:
            self.ticker_label.place_forget()
            self.ticker_label.after(1000, self.animate)

    def widget_update(self, *args):
        try:
            self.logger.debug('Updating ticker widget...')
            self.relx = args[0]
            self.rely = args[1]
            self.place(relx=self.relx, rely=self.rely)
            width = args[2]
            height = args[3]
            self.anchor = args[4]
            self.target_width = int(width * self.window_width)
            self.target_height = int(height * self.window_height)

            #self.configure(width=self.target_width - 3, height=self.target_height - 3)
            self.place(x=self.relx, y=self.rely)

            self.font_size = 50
            self.get_font_size()
            self.logger.debug('Widget has been updated!')
        except Exception as exc:
            self.logger.error(f'Cannot update the widget: {exc}')

    def destroy(self):
        self.logger.debug('Closing Ticker...')
        #self.destroy()

    def close_window(self, event):
        """ For testing purposes only."""
        sys.exit()
        #self.logger.debug('Escape key has been pressed, closing the window!')
        #self.window.destroy()

if __name__ == '__main__':
    try:
        window = Tk()
        window.title('Main Window')
        window.configure(bg='black')
        #window.attributes('-fullscreen',True)
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry("%dx%d+0+0" % (w, h))
        m = Ticker(window)
        window.bind('<Escape>', m.close_window)
        window.mainloop()
    except KeyboardInterrupt:
        window.destroy()

__version__ = '0.97' # 19th November 2020
__author__ = 'Dmitry Kudryashov'
__maintainer__ = 'Dmitry Kudryashov'
__email__ = "dmitry-kud@yandex.ru"    
__status__ = "Development"