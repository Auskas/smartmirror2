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

import os
import logging
from tkinter import *
from PIL import Image, ImageTk
import vlc
vlc.logger.setLevel(logging.CRITICAL)
import sys
import time
import requests
import urllib.request
import urllib.parse
import re
import time
from random import choice
import aiohttp
import asyncio
from multiprocessing import Process, Queue
import alsaaudio
    

class YoutubePlayer:

    def __init__(self, window, asyncloop, relx=0.48, rely=0.42, width=0.4, height=0.4, anchor='nw', show=True, default_video='Iron Maiden'):
        self.logger = logging.getLogger('SM2.youtube')
        self.loop = asyncloop

        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)

        self.logger.info('Initialization of YOUTUBE widget...')

        self.window = window

        # Dimesnsions of the main window (screen size)
        self.window_width = window.winfo_screenwidth()
        self.window_height = window.winfo_screenheight()

        self.target_width = int(width * self.window_width)
        self.target_height = int(height * self.window_height)
        self.anchor = anchor

        self.show = show

        self.icons_target_size = (
            int(self.target_width / 30), 
            int(self.target_width / 30)
        )

        self.relx = relx
        if self.anchor == 'ne':
            self.relx += width
        self.rely = rely

        self.default_video = default_video

        _isMacOS   = sys.platform.startswith('darwin')
        _isWindows = sys.platform.startswith('win')
        _isLinux = sys.platform.startswith('linux')
        args = ['--video-wallpaper', '--play-and-exit', '--verbose=1', '--logfile=vlc-log.txt',
                '--vout=X11', '--network-caching=1000', '--no-ts-trust-pcr', '--ts-seek-percent']
               #'--no-ts-trust-pcr', '--ts-seek-percent',  '--file-logging', '--logfile=vlc-log.txt', '--aout=alsa'
        if _isLinux:
            args.append('--no-xlib')
        
        # The timeout is used to initiate reloading of the video, 
        # for instance when the internet connection is lost.
        self.default_timeout = 30 #the number of seconds.
        self.timeout = self.default_timeout

        # Below are some Youtube links for testing purposes. Leave one uncommented to see it on the screen.
        #self.url = str('https://www.youtube.com/watch?v=r_izDyWAid4')
        self.url = ''
        self.instance = vlc.Instance(args)

        # Creating the media object (Youtube video URL).
        #self.media = self.instance.media_new(self.url)

        # Creating an instance of MediaList object and assigning it a tuple containing only one URL from Youtube.
        self.media_list = self.instance.media_list_new()

        self.audio = alsaaudio.Mixer()
        # Unmutes the system audio if it has been muted due to any errors.
        self.audio.setmute(0)
        self.audio_volume = self.audio.getvolume()[0] * 3

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
        self.widgetCanvas.place(
            relx=self.relx, 
            rely=self.rely + self.icons_target_size[0] / self.window_height, 
            anchor=self.anchor)

        # Set the window id where to render VLC's video output.
        self.widget_canvas_id = self.widgetCanvas.winfo_id()

        self.fullscreen_status = False

        self.set_window()
        self.saved_video_status = None

        self.external_command = None

        self.next_video_asyncio = False

        self.queue = Queue()
        receiver_loop = self.loop.create_task(self.process_receiver())
        status_loop = self.loop.create_task(self.status())

        if self.show:
            # Changes the video to the topic written in default_video
            initial_search_loop = self.loop.create_task(self.search(self.default_video))
        
        self.create_volume_bar()
        
        if __name__ == '__main__':
            self.loop.create_task(self.window_updater())

        self.logger.info('YOUTUBE widget has been initialized.')

    def create_volume_bar(self):

        self.volume_frame_width = self.target_width
        self.volume_frame_height = self.icons_target_size[0]
        # The range in pixels of the space between the muted speaker icon and the loud speaker to the right.
        self.volume_range = int(self.volume_frame_width - 3 * self.volume_frame_height)

        self.volume_frame = Canvas(self.window, width=self.volume_frame_width,
                                   height=self.volume_frame_height, bg='black',
                                   borderwidth=0, highlightbackground='black')

        self.volume_frame.place(
            relx=self.relx, 
            #rely=self.rely - self.icons_target_size[0], 
            rely=self.rely,
            anchor=self.anchor
            )

        # Loads the images, that are used in the widget, resizes them and assigns to the widget.
        image_bar = Image.open(f'{os.path.dirname(os.path.realpath(__file__))}{os.sep}icons{os.sep}volume_bar.png')
        image_bar = image_bar.resize((self.volume_range + self.volume_frame_height, self.icons_target_size[0]), Image.ANTIALIAS)
        render_bar = ImageTk.PhotoImage(image_bar)

        image_speaker = Image.open(f'{os.path.dirname(os.path.realpath(__file__))}{os.sep}icons{os.sep}speaker.png')
        image_speaker = image_speaker.resize(self.icons_target_size, Image.ANTIALIAS)
        render_speaker = ImageTk.PhotoImage(image_speaker)

        image_speaker_loud = Image.open(f'{os.path.dirname(os.path.realpath(__file__))}{os.sep}icons{os.sep}speaker_loud.png')
        image_speaker_loud = image_speaker_loud.resize(self.icons_target_size, Image.ANTIALIAS)
        render_speaker_loud = ImageTk.PhotoImage(image_speaker_loud)

        image_speaker_ball = Image.open(f'{os.path.dirname(os.path.realpath(__file__))}{os.sep}icons{os.sep}speaker_ball.png')
        image_speaker_ball = image_speaker_ball.resize(self.icons_target_size, Image.ANTIALIAS)
        render_speaker_ball = ImageTk.PhotoImage(image_speaker_ball)

        self.icon_speaker = Label(self.volume_frame, image=render_speaker, bg='black')
        self.icon_speaker.image = render_speaker

        self.icon_bar = Label(self.volume_frame, image=render_bar, bg='black')
        self.icon_bar.image = render_bar
        
        self.icon_speaker_ball = Label(self.volume_frame, image=render_speaker_ball, bg='black')
        self.icon_speaker.ball = render_speaker_ball

        self.icon_speaker_loud = Label(self.volume_frame, image=render_speaker_loud, bg='black')
        self.icon_speaker_loud.image = render_speaker_loud

        self.icon_speaker.place(relx=0, rely=0, anchor='nw')
        self.icon_bar.place(x=self.volume_frame_height, rely=0, anchor='nw')

        self.icon_speaker_loud.place(relx=1, rely=0, anchor='ne')

        self.volume_widget_timeout = 0
        self.volume_widget_concealed = False
        self.volume_widget_hide()        

    def volume_widget_show(self):
        self.volume_frame.config(width=self.volume_frame_width, 
                                 height=self.volume_frame_height)
        self.volume_widget_concealed = False

    def volume_widget_hide(self):
        self.volume_frame.config(width=0, height=0)
        self.volume_widget_concealed = True

    def volume_widget_ball_position(self, volume):
        #self.icon_speaker.place(relx=0, rely=0, anchor='nw')
        #self.icon_bar.place(x=self.volume_frame_height, rely=0, anchor='nw')

        self.speaker_ball_position_absolute = round((volume * self.volume_range) / 100) + self.volume_frame_height
        self.icon_speaker_ball.place(x=self.speaker_ball_position_absolute, rely=0, anchor='nw')

        #self.icon_speaker_loud.place(relx=1, rely=0, anchor='ne')

    def video_fullscreen_status(self):
        """ The method is used to place the widget back either in the fullscreen or windowed mode
            based on the mode when the playback is stopped.
            In other words, if the widget is in the fullscreen mode when the playback is stopped,
            it will be in the fullscreen mode after resuming the playback and vice versa."""
        if self.fullscreen_status:
            self.widgetCanvas.place(relx=0, rely=0, anchor='nw')
            self.widgetCanvas.config(width=self.window_width, height=self.window_height)
        else:
            self.widgetCanvas.place(relx=self.relx, rely=self.rely, anchor=self.anchor)
            self.widgetCanvas.config(width=self.video_window_width, height=self.video_window_height)

    def mute(self):
        self.audio.setmute(1)

    def unmute(self):
        self.audio.setmute(0)

    def play(self):
        self.list_player.play()
        self.video_status = 'running'

    def stop(self):
        """ The method as if stops the playback of the widget. In fact it pauses the playback and changes
            its size to zero."""
        self.widgetCanvas.config(width=0, height=0)
        self.list_player.pause()
        self.video_status = 'stopped'

    async def next_video(self):
        try:
            self.next_video_asyncio = True
            self.list_player.pause()
            self.list_player.next()
            await asyncio.sleep(3)
            self.list_player.play()
            self.next_video_asyncio = False
        except Exception as exc:
            self.logger.error(f'Cannot play the next video: {exc}')
            
    async def search(self, topic):
        """ The method is used to get Youtube link of the desired topic.
            It loads the webpage using a proper request and finds the URL of the most relevant video.
            At the end it calls change_url method to actually change the URL.
            Arguments: topic as a string."""

        self.logger.debug(f'Youtube URL searching for {topic}...')
        query_string = urllib.parse.urlencode({"search_query" : topic})
        link = "http://www.youtube.com/results?" + query_string

        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(link) as resp:
                    if resp.status != 200:
                        self.logger.error(f'Cannot get {link}.\n Status {resp.status}')
                    else:
                        self.logger.debug(f'{link} loaded')
                        results = await resp.text()
                        results_parser_process = Process(target=self.process_results, args=(results, ))
                        results_parser_process.start()
        except Exception as error:
            self.logger.error(f'Cannot load the Youtube page: {error}')
            await asyncio.sleep(20)
            search_loop = self.loop.create_task(self.search(topic))


    def process_results(self, resp):
        try:
            search_results = re.findall(r'"url":"\/watch\?v=(.{11})"', resp)
            if len(search_results) > 0:
                self.logger.debug('Found the URLs for the requested video...')
                # Puts all the found videos into the queue.
                #for search_result in search_results:
                    #self.queue.put("https://www.youtube.com/watch?v=" + search_result)
                self.queue.put(search_results)
            else:
                self.logger.debug(f'Search results are empty.')
                self.queue.put(None)
        except Exception as exc:
            self.logger.error(f'Cannot process the search results : {exc}')

    async def process_receiver(self):
        while True:
            if self.queue.empty():
                await asyncio.sleep(1)
            else:
                urls = self.queue.get()
                if urls is not None:
                    self.change_url(urls)            

    def change_url(self, urls):
        """ The method is used to change video's URL.
        It stops the player, creates a media object with the requested source,
        creates a list of media containing only one media and
        associates the list to the player. Afterwards the player restarts.
        Arguments: url as a string."""
        
        # In order to change the video, the script pauses the player, removes the first (and only) video
        # from the media list, adds target URL to the media list, virtually presses next video in
        # the player and finally resumes the playback.

        try:
            self.list_player.stop()

            # Clears the media list instance from all the containing videos.
            self.media_list.release()
            self.logger.debug('Media list has been cleared: ') 

            self.media_list = self.instance.media_list_new()
            for url in urls:
                url = "https://www.youtube.com/watch?v=" + url
                self.media_list.add_media(url)
            self.logger.debug(f'{self.media_list.count()} urls have been added to Media list!')

            self.list_player.set_media_list(self.media_list)

            self.list_player.next()

            self.player.set_xwindow(self.widget_canvas_id)

            self.list_player.play()

            self.video_status = 'running'

            self.logger.debug('The URL has been changed.')
        except Exception as exc:
            self.logger.error(f'Cannot update the media list and change the URL: {exc}')

    def set_window(self):
        """ The method is used to change the size of the video canvas.
        The canvas occupies only small part of the main window."""
        try:
            self.logger.debug('Setting video in WINDOW mode...')
            self.widgetCanvas.place(
                relx=self.relx, 
                rely=self.rely + self.icons_target_size[0] / self.window_height, 
                anchor=self.anchor)
            self.widgetCanvas.config(width=self.target_width, height=self.target_height)
            self.player.set_xwindow(self.widget_canvas_id)
            self.fullscreen_status = False
            self.video_status = 'running'
        except Exception as exc:
            self.logger.error(f'Cannot set video in WINDOW mode: {exc}')

    def set_fullscreen(self):
        """ The method is used to change the size of the video canvas.
        The canvas size equals to the size of the screen.
        Therefore it occupies the whole screen."""
        try:
            self.logger.debug('Setting video in FULLSCREEN mode...')
            self.widgetCanvas.place(relx=0, rely=0, anchor='nw')
            self.widgetCanvas.config(width=self.window_width, height=self.window_height)
            self.player.set_xwindow(self.widget_canvas_id)

            # Makes the widget appear on top of the others.
            self.window.lift(self.widgetCanvas)

            self.fullscreen_status = True
            self.video_status = 'running'
        except Exception as exc:
            self.logger.error(f'Cannot set video in FULLSCREEN mode: {exc}')

    def widget_update(self, *args):
        try:
            self.logger.debug('Updating Youtube widget...')
            # !!! Stop video before updating the widget.
            self.list_player.stop()

            width = args[2]
            height = args[3]
            self.anchor = args[4]
            self.target_width = int(width * self.window_width)
            self.target_height = int(height * self.window_height)
            self.icons_target_size = (
                int(self.target_width / 30), 
                int(self.target_width / 30)
            )

            self.relx = args[0]
            if self.anchor == 'ne':
                self.relx += width
            self.rely = args[1] + self.icons_target_size[0] / self.window_height

            self.volume_frame_width = self.target_width
            self.volume_frame_height = self.icons_target_size[0]
            # The range in pixels of the space between the muted speaker icon and the loud speaker to the right.
            self.volume_range = int(self.volume_frame_width - 3 * self.volume_frame_height)
            
            self.volume_frame.place(
                relx=self.relx, 
                rely=self.rely,
                anchor=self.anchor
                )        

            if self.fullscreen_status == False:
                self.set_window()

            search_loop = self.loop.create_task(self.search(args[5]))
            self.logger.debug('Widget has been updated!')
        except Exception as exc:
            self.logger.error(f'Cannot update the widget: {exc}')


    async def status(self):
        self.previous_time = 0
        while True:
            # The following condition is used to check if the video is being played.
            # In case of the connection lost it decrements the timeout until it reaches
            # zero and tries to restart the video.
            if self.show:
                try:
                    self.current_time = self.player.get_time()
                    if self.current_time == self.previous_time:
                        #print(self.current_time)
                        self.timeout -= 0.05
                        if self.timeout <= 0:
                            self.logger.error(f'Probably the internet connection has been lost. Trying to reload...')
                            self.timeout = self.default_timeout
                            self.list_player.pause()
                            self.list_player.next()
                            self.list_player.play()
                    else:
                        self.timeout = self.default_timeout
                    self.previous_time = self.current_time
                except Exception as exc:
                    self.logger.error(f'Cannot reload video: {exc}')

                try:
                    if self.external_command == 'next_video' and self.next_video_asyncio == False:
                        next_video_task = self.loop.create_task(self.next_video())

                    if self.external_command == 'volume_down':
                        self.audio_volume -= 1
                        if self.audio_volume < 0:
                            self.audio_volume = 0
                        self.audio.setvolume(int(self.audio_volume // 3))
                        self.volume_widget_ball_position(self.audio_volume // 3)

                    elif self.external_command == 'volume_up':
                        self.audio_volume += 1
                        if self.audio_volume > 300:
                            self.audio_volume = 300
                        self.audio.setvolume(int(self.audio_volume // 3))
                        self.volume_widget_ball_position(self.audio_volume // 3)

                    if self.external_command in ('volume_up', 'volume_down') and self.volume_widget_concealed:
                        self.volume_widget_timeout = 20
                        self.volume_widget_show()

                    elif self.external_command not in ('volume_up', 'volume_down') and self.volume_widget_concealed == False:
                        if self.volume_widget_timeout == 0:
                            self.volume_widget_hide()
                        else:
                            self.volume_widget_timeout -= 1

                    self.external_command = None
                except Exception as exc:
                    self.logger.error(f'Cannot execute widget gestures controls: {exc}')

                await asyncio.sleep(0.05)
            else:
                if self.video_status == 'running':
                    self.stop()
                await asyncio.sleep(1)

    async def window_updater(self):
        """ This method is used only if the module is executed directly.
            Updates the tkinter window."""
        interval = 1/120
        while True:
            self.window.update()
            await asyncio.sleep(interval)


    async def process_receiver_main(self, queue):
        """ The method is asynchronously waits for strings in the queue."""
        while True:
            if queue.empty():
                await asyncio.sleep(1)
            else:
                data = queue.get()
                try:
                    for key in data.keys():
                        if key == 'detected_gesture':
                            if data[key] == 'pointing_finger':
                                self.external_command = 'volume_down'
                            elif data[key] == 'sign_of_the_horns':
                                self.external_command = 'volume_up'
                            else:
                                self.external_command = False
                        elif key == 'face_detected':
                            self.face_detected = data[key]
                        else:
                            self.face_detected = False
                            self.gesture = False
                except Exception as exc:
                    self.logger.warning(f'Cannot process the data in the queue {exc}')

    def destroy(self):
        self.logger.debug('Closing Youtube...')
        self.list_player.stop()
        self.media_list.release()

if __name__ == '__main__':
    try:
        loop = asyncio.get_event_loop()
        window = Tk()
        window.title('Youtube')
        window.configure(bg='black')
        #window.overrideredirect(True)
        w, h = window.winfo_screenwidth(), window.winfo_screenheight()
        window.geometry("%dx%d+0+0" % (w, h))

        youtube = YoutubePlayer(window, loop)
        youtube.set_fullscreen()
        
        #import cv2
        #import importlib.util
        #spec = importlib.util.spec_from_file_location("gestures.py", "/media/data/sm2/smartmirror2/gestures.py")
        #gestures = importlib.util.module_from_spec(spec)
        #spec.loader.exec_module(gestures)
        

        from multiprocessing import Process, Queue
        #cam = cv2.VideoCapture(0)
        queue = Queue()
        #gestures_recognizer = gestures.GesturesRecognizer(cam, queue)
        #gestures_recognizer_process = Process(target=gestures_recognizer.tracker).start()

        loop.create_task(youtube.process_receiver_main(queue))
        loop.run_forever()
        

    except KeyboardInterrupt:
        sys.exit()

__version__ = '0.97' # 19th November 2020
__author__ = 'Dmitry Kudryashov'
__maintainer__ = 'Dmitry Kudryashov'
__email__ = "dmitry-kud@yandex.ru"    
__status__ = "Development"