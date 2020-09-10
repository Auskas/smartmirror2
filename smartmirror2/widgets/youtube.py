#!/usr/bin/python3
# youtube.py
#
# The main goal of the module is to create a widget that is used to play Youtube videos.
# An instance of the Youtuber class follows the updates of detected voice commands and gestures.
#
# The playback can be switched to full screen, returned back to its initial windowed size,
# stopped, paused or resumed. The commands are saved in a set at voiceAssistant.cmd['youtube'].
# The following commands are tracked (they are self-explanetary): 'fullscreen', 'window',
# 'playback stop', 'playback resume', 'playback pause'.
#
# A dedicated voice command is used to search the most relevant video on Youtube: 'video search [topic]'
#
# The pointing finger gesture controls the volume - a volume bar appears on top of the playback widget.
# Moving the finger to the left and right turns the volume down and up accordingly.

import logging
from tkinter import *
import vlc
print(vlc.__file__)
vlc.logger.setLevel(logging.CRITICAL)
import sys
import time
import threading
import requests
import urllib.request
import urllib.parse
import re
import time
from random import choice
import threading
#import alsaaudio
    

class YoutubePlayer:

    def __init__(self, window, relx=0.48, rely=0.42, width=0.4, height=0.4, anchor='nw'):
        self.logger = logging.getLogger('SM.youtube')

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

        print(self.target_width, self.target_height)

        _isMacOS   = sys.platform.startswith('darwin')
        _isWindows = sys.platform.startswith('win')
        _isLinux = sys.platform.startswith('linux')
        args = ['--video-wallpaper', '--play-and-exit', '--verbose=0', '--logfile=vlc-log.txt',
                '--vout=X11', '--network-caching=1000', '--no-ts-trust-pcr', '--ts-seek-percent']
               #'--no-ts-trust-pcr', '--ts-seek-percent',  '--file-logging', '--logfile=vlc-log.txt', '--aout=alsa'
        if _isLinux:
            args.append('--no-xlib')
        # Below are some Youtube links for testing purposes. Leave one uncommented to see it on the screen.
        #self.url = str('https://www.youtube.com/watch?v=9Auq9mYxFEE') # Sky News
        #self.url = str('https://www.youtube.com/watch?v=fdN46JyP1lI') # Football Club 1
        #self.url = str('https://www.youtube.com/watch?v=-fLF_ejuOjs&pbjreload=10') # Football Club 2
        #self.url = str('https://www.youtube.com/watch?v=P-_lx0ysHfw') # Spartak
        #self.url = str('https://www.youtube.com/watch?v=diRtRhcaUNI') # Metallica
        self.url = str('https://www.youtube.com/watch?v=2MISe09ArHw')
        #self.url = str('https://www.youtube.com/watch?v=RjIjKNcr_fk') # Al Jazeera
        #self.url = str('https://www.youtube.com/watch?v=dI4jr5HyuT0') # NTV Russia live

        self.instance = vlc.Instance(args)

        # Creating the media object (Youtube video URL).
        #self.media = self.instance.media_new(self.url)

        # Creating an instance of MediaList object and assigning it a tuple containing only one URL from Youtube.
        self.media_list = self.instance.media_list_new((self.url, ))

        # Creating an instance of the player.
        self.player = self.instance.media_player_new()
        self.player.audio_set_volume(100)

        # Creating a new MediaListPlayer instance and associating the player and playlist with it.
        self.list_player = self.instance.media_list_player_new()
        self.list_player.set_media_player(self.player)
        self.list_player.set_media_list(self.media_list)

        # Videos are played in the canvas, which size can be adjusted in order to show it in the fullscreen mode.
        self.widgetCanvas = Canvas(self.window, width=self.target_width,
                                   height=self.target_height, bg='black',
                                   borderwidth=0, highlightbackground='black')
        self.widgetCanvas.place(relx=self.relx, rely=self.rely, anchor=self.anchor)

        # Set the window id where to render VLC's video output.
        self.widget_canvas_id = self.widgetCanvas.winfo_id()
        #self.player.set_xwindow(self.widget_canvas_id)
        #self.player.set_fullscreen(False)

        self.fullscreen_status = False

        #if sys.platform != 'win32':
            #self.audio = alsaaudio.Mixer()
            #self.audio_volume = self.audio.getvolume()[0] # system audio volume
            #self.logger.debug(f'Audio volume {self.audio_volume}')

        #self.list_player.play()
        self.set_window()
        self.saved_video_status = None
        self.logger.info('Youtube widget has been initialized.')

    def video_fullscreen_status(self):
        """ The method is used to place the widget back either in the fullscreen or windowed mode
            based on the mode when the playback is stopped.
            In other words, if the widget is in the fullscreen mode when the playback is stopped,
            it will be in the fullscreen mode after resuming the playback and vice versa."""
        if self.fullscreen_status:
            self.widgetCanvas.place(relx=0, rely=0, anchor='nw')
            self.widgetCanvas.config(width=self.w, height=self.h)
        else:
            self.widgetCanvas.place(relx=self.relx, rely=self.rely, anchor=self.anchor)
            self.widgetCanvas.config(width=self.video_window_width, height=self.video_window_height)

    def play(self):
        self.list_player.play()
        self.video_status = 'running'

    def stop(self):
        """ The method as if stops the playback of the widget. In fact it pauses the playback and changes
            its size to zero."""
        self.widgetCanvas.config(width=0, height=0)
        self.list_player.pause()
        self.video_status = 'stopped'

    def search(self, topic):
        """ The method is used to get Youtube link of the desired topic.
            It loads the webpage using a proper request and finds the URL of the most relevant video.
            At the end it calls change_url method to actually change the URL.
            Arguments: topic as a string."""

        self.logger.debug(f'Youtube URL searching for {topic}...')
        query_string = urllib.parse.urlencode({"search_query" : topic})

        try:
            res = requests.get("http://www.youtube.com/results?" + query_string)
            if res.status_code == 200:
                search_results = re.findall(r'"url":"\/watch\?v=(.{11})"', res.text)
            else:
                search_results = []
        except Exception as error:
            self.logger.debug(f'Cannot load Youtube: {error}')

        if len(search_results) > 0:
            self.logger.debug('Found the URL for the requested video...')
            self.change_url("https://www.youtube.com/watch?v=" + search_results[0])
        else:
            self.logger.debug(f'Search results are empty.')

    def change_url(self, url):
        """ The method is used to change video's URL.
        It stops the player, creates a media object with the requested source,
        creates a list of media containing only one media and
        associates the list to the player. Afterwards the player restarts.
        Arguments: url as a string."""
        self.logger.debug(f'Changing URL of the media player: {url}')
        # In order to change the video, the script pauses the player, removes the first (and only) video
        # from the media list, adds target URL to the media list, virtually presses next video in
        # the player and finally resumes the playback.
        self.list_player.pause()

        self.media_list.remove_index(0)
        self.media_list.add_media(url)
        self.list_player.next()

        self.player.set_xwindow(self.widget_canvas_id)

        self.list_player.play()

        self.video_status = 'running'

        self.logger.debug('The URL has been changed.')

    def set_window(self):
        """ The method is used to change the size of the video canvas.
        The canvas occupies only small part of the main window."""
        self.widgetCanvas.place(relx=self.relx, rely=self.rely, anchor=self.anchor)
        self.widgetCanvas.config(width=self.target_width, height=self.target_height)
        self.player.set_xwindow(self.widget_canvas_id)
        self.fullscreen_status = False
        self.video_status = 'running'

    def set_fullscreen(self):
        """ The method is used to change the size of the video canvas.
        The canvas size equals to the size of the screen.
        Therefore it occupies the whole screen."""
        self.widgetCanvas.place(relx=0, rely=0, anchor='nw')
        self.widgetCanvas.config(width=self.w, height=self.h)
        self.player.set_xwindow(self.widget_canvas_id)
        self.fullscreen_status = True
        self.video_status = 'running'

    def update(self, *args):
        self.relx = args[0]
        self.rely = args[1]
        width = args[2]
        height = args[3]
        self.anchor = args[4]
        self.target_width = int(width * self.window_width)
        self.target_height = int(height * self.window_height)
        if self.fullscreen_status == False:
            self.set_window()


if __name__ == '__main__':
    try:
        window = Tk()
        window.title('Youtube')
        window.configure(bg='black')
        #window.overrideredirect(True)
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry("%dx%d+0+0" % (w, h))
        youtube = YoutubePlayer(window)     
        youtube_thread = threading.Thread(target=youtube.play)
        youtube_thread.start()      
        #youtube.search('Corey Schafer Django')
        window.mainloop()
    except KeyboardInterrupt:
        sys.exit()
    print('Alles')