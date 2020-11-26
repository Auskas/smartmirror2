from tkinter import *

def animate():   
    if ticker_label.winfo_x() > -ticker_label.winfo_width():
        ticker_label.place(x=ticker_label.winfo_x() - TICKER_SPEED)
    else:
        print('ALLES!')
        ticker_label.place(x=x_limit)
    ticker_label.after(REFRESH_RATE, animate)

gui = Tk()
gui.geometry('8000x100+1+600')                 
gui.title('TEST')
gui.config (bg = 'blue')                

ticker_label = Label(gui, text = 'Владимир Путин сообщил, что он устал и уходит!')
ticker_label.config (fg = 'white', bg = 'blue', font=('times','60'))

x_limit = gui.winfo_screenwidth()
print(x_limit)
TICKER_SPEED = 1
REFRESH_RATE = 10
ticker_label.place(x=x_limit)
animate()
gui.mainloop()