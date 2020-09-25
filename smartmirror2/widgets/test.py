import vlc
from tkinter import *
import threading
import ctypes
import os

LEVELS = {
    0: 'DEBUG', 
    2: 'NOTICE', 
    3: 'WARNING', 
    4: 'ERROR'
    }

libc = ctypes.cdll.LoadLibrary("libc.{}".format("so.6" if os.uname()[0] == 'Linux' else "dylib"))

def youtuber(url, window):

    widgetCanvas = Canvas(
        window, 
        width=640,
        height=360, 
        bg='black',
        borderwidth=0, 
        highlightbackground='black'
    )

    widgetCanvas.place(
        relx=0.5, 
        rely=0.5, 
        anchor='ne')

    # Set the window id where to render VLC's video output.
    widget_canvas_id = widgetCanvas.winfo_id()

    instance = vlc.Instance("--no-xlib")

    media_list = instance.media_list_new((url, ))

    player = instance.media_player_new()

    list_player = instance.media_list_player_new()
    list_player.set_media_player(player)
    list_player.set_media_list(media_list)

    list_player.play()

    player.set_xwindow(widget_canvas_id)
    instance.log_set(log_handler, None)

@vlc.CallbackDecorators.LogCb
def log_handler(instance, log_level, ctx, fmt, va_list):
    #if log_level < 3:
        #return
    bufferString = ctypes.create_string_buffer(4096)
    libc.vsprintf(bufferString, fmt, ctypes.cast(va_list, ctypes.c_void_p))
    msg = bufferString.value.decode('utf-8')
    module, _file, _line = vlc.libvlc_log_get_context(ctx)
    module = module.decode('utf-8')
    if module == 'vlcpulse':
        return
    try:
        print(u"log_level={log_level}, module={module}, msg={msg}".format(log_level=log_level, module=module, msg=msg))
    except Exception as e:
        logger.exception(e)


    # Print it out, or do something else
    #print('LOG: ' + fmt + args)

if __name__ == '__main__':
    url = str('https://www.youtube.com/watch?v=jrOxsjdeccw&t=357s')
    
    window = Tk()
    window.title('Main Window')
    window.configure(bg='black')
    #window.overrideredirect(True)
    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    window.geometry("%dx%d+0+0" % (w, h))
    youtuber(url, window)
    #errors_thread = threading.Thread(target=_errors).start()

    window.mainloop()