#!/usr/bin/python3
# ticker.py - a ticker for my Smart Mirror Project.

from tkinter import *
import datetime
import logging

class Ticker(Canvas):

    def __init__(self, window, relx=0.0, rely=0.93, width=0.97, height=0.05, anchor='nw', show=True, fps=125):
        # Special news ticker for April's Fool day.
        self.april_fools_news = 'Владимир Путин выступил на Генеральной ассамблее ООН в костюме Деда Мороза.   ***   Дмитрий Медведев в ходе своего визита на Дальний восток заявил о невозможности разблокировки своего айфона.   ***  Укробандеровские собакофашисты вновь нарушили перемирие на Донбасе, коварно атаковав позиции отважных ополченцев.   ***    В ходе военных учений в Калининградской области российские войска уничтожили двести танков и триста самолетов противника. Условного.   ***   Президент России заявил о двухкратном снижении темпов прироста скорости падения российской экономики.   ***   Согласно опроса ФГЛПРФ ЗД более половины респондентов заявили о беззаговорочной поддержке курса Президента. Кормильца нашего, храни его Бог, благослави все дела его праведные.   ***   Виталий Мутко во время встречи со студентами МГУ признался, что только искренняя любовь к Отчизне заставляет его оставаться на своём посту.   ***   Глава МИД России Сергей Лавров считает овец перед сном.   ***   "Патриотизм и любовь к Родине обязаны быть в сердце каждого россиянина", - заявил Игорь Сечин на встрече с гостями и журналистами на борту своей яхты в Монте-Карло.   ***   Патриарх Московский и Всея Руси Кирилл считает, что российскому обществу следует отказаться от чрезмерной роскоши. В пользу РПЦ.'
        self.news_string = '   *** Загрузка новостей ***   '
        self.logger = logging.getLogger('SM.ticker')

        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)

        self.font_size = 40

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

        # borderwidth default size is 2 (we don't need any borders), highlightbackground default is white - when the canvas is not in the focus.
        Canvas.__init__(
            self, window,  
            bg='black', 
            borderwidth=0, 
            highlightbackground='black'
        )

        # The following variable 'fps' is used to determine the speed of the ticker.
        self.fps = fps

        self.text_id = self.create_text(
            0, 
            0, 
            text=self.april_fools_news, 
            anchor=self.anchor, 
            fill='lightblue', 
            font=("SFUIText", self.font_size, "bold"), 
            tags=("text",)
        )
        (x0, y0, x1, y1) = self.bbox("text")
        self.configure(width=self.target_width - 3, height=self.target_height - 3)
        self.place(relx=self.relx, rely=self.rely)
        self.logger.debug('An instance of Ticker widget has been created.')
        self.get_font_size()
        self.animate()

    def get_font_size(self):
        """ The method decreases the font size until it satisfies the target
            width and height of the widget."""
        try:
            self.itemconfig(self.text_id, text=self.april_fools_news)
            self.coords("text", 0, 0)
            while self.font_size > 12:
                self.itemconfig(self.text_id, font=("SFUIText", self.font_size, "bold"))
                x0 = self.winfo_width()
                y0 = int(self.winfo_height()/2)
                self.coords("text", 0, y0)
                (x0, y0, x1, y1) = self.bbox("text")
                if y1 > self.target_height:
                    self.font_size -= 1
                else:
                    self.itemconfig(self.text_id, text=self.news_string)
                    #self.logger.debug(f'Target widget width {self.target_width}')
                    #self.logger.debug(f'Real widget width {self.winfo_width()}')
                    #self.logger.debug(f'Target widget height {self.target_height}')
                    #self.logger.debug(f'Real widget height {self.winfo_height()}')
                    break
                self.update()
        except Exception as exc:
            self.logger.error(f'Cannot adjust the size of the widget: {exc}')

    def animate(self):
        if self.show == False:
            self.place_forget()
            self.after_id = self.after(1000, self.animate)
        else:
            (x0, y0, x1, y1) = self.bbox("text")

            # The text is off the screen. Resetting the x while also getting the news from newsruBot.
            if x1 < 0 or y1 < 0:
                current_time = datetime.datetime.utcnow() + datetime.timedelta(hours=3)
                # Special news ticker for April Fools' Day.
                if current_time.month == 4 and current_time.day == 1:
                    text = self.april_fools_news

                # Regular news ticker.
                else:
                    text = self.news_string
                self.itemconfig(self.text_id, text=text, anchor=self.anchor)
                x0 = self.relx + self.winfo_width()
                y0 = int(self.winfo_height() / 2)
                self.coords("text", x0, y0)
                self.after_id = self.after(int(1000/self.fps), self.animate)

            # Moves the ticker one pixel to the left each 1000/fps millisecond.
            else:
                self.move("text", -1, 0)
                self.after_id = self.after(int(1000/self.fps), self.animate)

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
            self.place(relx=self.relx, rely=self.rely)

            self.font_size = 30
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
        window.attributes('-fullscreen',True)
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry("%dx%d+0+0" % (w, h))
        m = Ticker(window)
        m.news_string = m.april_fools_news
        window.bind('<Escape>', m.close_window)
        window.mainloop()
    except KeyboardInterrupt:
        window.destroy()

__version__ = '0.97' # 19th November 2020
__author__ = 'Dmitry Kudryashov'
__maintainer__ = 'Dmitry Kudryashov'
__email__ = "dmitry-kud@yandex.ru"    
__status__ = "Development"