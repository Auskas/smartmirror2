#!usr/bin/python3
# voice_assistant.py - voice assistant for my Smart Mirror project.

import logging
import speech_recognition as sr
import os
import time

class VoiceAssistant():
    
    def __init__(
        self,
        WIDGETS_CONFIG,
        queue       
    ):
    
        self.logger = logging.getLogger('SM.voice_assistant')
        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)

        self.speech_recognizer = sr.Recognizer()

        #print(sr.Microphone.list_microphone_names())

        self.queue = queue

        self.cmd = {}

        for key in WIDGETS_CONFIG.keys():
            self.cmd[WIDGETS_CONFIG[key]['name']] = WIDGETS_CONFIG[key]['show']

        self.hide_commands = (
            'убрать', 
            'убери', 
            'скрыть', 
            'скрой', 
            'закрыть', 
            'закрой', 
            'выключи', 
            'выключить', 
            'hide', 
            'conceal', 
            ' off', 
            'remove'
        )
        
        self.show_commands = (
            'показать', 
            'покажи', 
            'вывести', 
            'выведи',
            'открой', 
            'открыть', 
            'включи', 
            'включить', 
            'show', 
            'open', 
            ' on', 
            'watch', 
            'play'
        )

        self.logger.info('Voice assistant has been initialized!')
        

    def listen(self):
        self.logger.info('Listening to the microphone...')
        with sr.Microphone(sample_rate=16000, chunk_size=1024) as source:
            # Represents the minimum length of silence (in seconds) that will register as the end of a phrase (type: float).
            self.speech_recognizer.pause_threshold = 1
            # The duration parameter is the maximum number of seconds that it will dynamically adjust the threshold for before returning.
            #This value should be at least 0.5 in order to get a representative sample of the ambient noise.
            #self.speech_recognizer.dynamic_energy_threshold = False
            self.speech_recognizer.adjust_for_ambient_noise(source, duration=0.5)
            try:
                audio = self.speech_recognizer.listen(source, timeout=3, phrase_time_limit=3)
                
                #self.message_label.config(text='CONFIG')
                self._recognize(audio)
            # Catches the exception when there is nothing said during speech recognition.
            except sr.WaitTimeoutError:
                self.logger.debug('Timeout: no speech has been registred.')
                self.queue.put({'voice_assistant' : False})
            except Exception as exc:
                self.logger.debug(f'Cannot get the mic: {exc}')
                self.queue.put({'voice_assistant' : False})

    def _recognize(self, audio):
        self.logger.info('Trying to recognize speech...')
        try:
            user_speech = self.speech_recognizer.recognize_google(audio, language = "en-EN").lower()
            self.logger.debug(f'User said: {user_speech}')
            self.cmd_handler(user_speech)
        except sr.UnknownValueError:
            self.logger.info('Cannot recognize speech...')
            self.queue.put({'voice_assistant' : False})
            
    def cmd_handler(self, cmd):
        """ Gets a string of recognized speech as cmd. 
            Checks if there are any sort of commands in it.
            Modifies self.cmd according to the detected commands."""

        self.logger.info('Looking for commands in the speech...')
        if self.second_part_command(cmd) == False and \
            (
            cmd.find('все виджеты') != -1 or \
            cmd.find('all the widgets') != -1 or \
            cmd.find('all widgets') != -1 or \
            cmd.find('всю графику') != -1 or \
            cmd.find('всё') != -1
            ):

            for key in self.cmd.keys():
                self.cmd[key] = False

            #self.logger.debug('All the widgets have been concealed!')

        elif self.second_part_command(cmd) and \
            (
            cmd.find('все виджеты') != -1 or \
            cmd.find('all the widgets') != -1 or \
            cmd.find('всю графику') != -1 or \
            cmd.find('всё') != -1
            ):

            for key in self.cmd.keys():
                self.cmd[key] = True

            #self.logger.debug('All the widgets is being showing!')

        elif cmd.find('установить громкость') != -1:
            try:
                self.cmd['playback_volume'] = int(cmd[cmd.rfind('установить громкость') + len('установить громкость ') + 1:])
            except exception as error:
                self.logger.error('Cannot convert volume control value into an integer.')

        elif (cmd.find('часы') != -1 or cmd.find('clock') != -1) and \
              self.second_part_command(cmd) == False:
            self.cmd['clock'] = False

        elif (cmd.find('часы') != -1 or cmd.find('clock') != -1) and \
              self.second_part_command(cmd):
            self.cmd['clock'] = True

        elif (cmd.find('погод') != -1 or cmd.find('weather') != -1) and \
              self.second_part_command(cmd) == False:
            self.cmd['weather'] = False

        elif (cmd.find('погод') != -1 or cmd.find('weather') != -1) and \
              self.second_part_command(cmd):
            self.cmd['weather'] = True
            
        elif (cmd.find('курс') != -1 or cmd.find('stocks') != -1) and \
              self.second_part_command(cmd) == False:
            self.cmd['stocks'] = False

        elif (cmd.find('курс') != -1 or cmd.find('stocks') != -1) and \
              self.second_part_command(cmd):
            self.cmd['stocks'] = True
            
        elif (cmd.find('спартак') != -1 or cmd.find('spartak') != -1) and \
              self.second_part_command(cmd) == False:
            self.cmd['spartak'] = False

        elif (cmd.find('спартак') != -1 or cmd.find('spartak') != -1) and \
              self.second_part_command(cmd):
            self.cmd['spartak'] = True
            
        elif self.second_part_command(cmd) == False and \
              (cmd.find('строк') != -1 or cmd.find('ticker') != -1):
            self.cmd['marquee'] = False

        elif self.second_part_command(cmd) and \
            (cmd.find('строк') != -1 or cmd.find('ticker') != -1):
            self.cmd['marquee'] = True

        elif (cmd.find('вирус') != -1 or cmd.find('covid') != -1) and \
              self.second_part_command(cmd) == False:
            self.cmd['covid'] = False

        elif (cmd.find('вирус') != -1 or cmd.find('covid') != -1) and \
              self.second_part_command(cmd):
            self.cmd['covid'] = True
            
        elif cmd.find('полный экран') != -1 or \
             cmd.find('весь экран') != -1 or \
             cmd.find('развернуть') != -1 or \
             cmd.find('full screen') != -1 or \
             cmd.find('fullscreen') != -1:
            self.cmd['youtube_fullscreen'] = True
        
        elif cmd.find('убрать') != -1 or \
             cmd.find('окно') != -1 or \
             cmd.find('в угол') != -1 or \
             cmd.find('свернуть') != -1 or \
             cmd.find('window') != -1:
            self.cmd['youtube_fullscreen'] = False
            
        elif (
             cmd.find('видео') != -1 or \
             cmd.find('video') != -1 or \
             cmd.find('playback') != -1
             ) and \
             (
             cmd.find('стоп') != -1 or \
             cmd.find('остановить') != -1 or \
             cmd.find('stop') != -1
             ):
            self.cmd['youtube_stop'] = True
        
        elif (
            cmd.find('видео') != -1 or \
            cmd.find('video') != -1 or \
            cmd.find('playback') != -1
            ) and \
            (
            cmd.find('пауза') != -1 or \
            cmd.find('pause') != -1
            ):
            self.cmd['youtube_pause'] = True
        
        elif (
            cmd.find('видео') != -1 or \
            cmd.find('video') != -1 or \
            cmd.find('playback') != -1
            ) and \
            (
            cmd.find('возобновить') != -1 or \
            cmd.find('play') != -1 or \
            cmd.find('продолжить') != -1 or \
            cmd.find('resume') != -1
            ):
            self.cmd['youtube_play'] = True
        
        # Youtube video search condition, for instance 'watch youtube Metallica', 
        # 'show video Liverpool Manchester City' 
        elif self.second_part_command(cmd) and \
            (
            cmd.find('youtube') != -1 or \
            cmd.find('video') != -1 or \
            cmd.find('видео') != -1 or \
            cmd.find('ютюб') != -1 or \
            cmd.find('ютуб') != -1
            ):
            for c in self.show_commands:
                if cmd.find(c) != -1:
                    cmd = cmd[cmd.find(cmd):]
                    cmd = cmd.replace(c, '')
            self.cmd['youtube_search'] = cmd

        if len(self.cmd) > 0:
            self.logger.debug(f'The following commands will be processed: {self.cmd}')
            self.cmd['raw_string'] = cmd
            self.queue.put({'voice_assistant' : self.cmd})
            self.cmd = {}
          
    def second_part_command(self, cmd):
        """ Method checks if there is a word in the voice command associated with showing or
            concealing a widget.
            Returns True if there is a word associated with showing a widget.
            Returns False if there is a word associated with concealing a widget.
            Otherwise, returns None."""
        for c in self.hide_commands:
            if cmd.find(c) != -1:
                return False
        for c in self.show_commands:
            if cmd.find(c) != -1:
                return True
        return None        

if __name__ == '__main__':

    from tkinter import *
    from widgets.voice_assistant_widget import VoiceAssistantWidget

    window = Tk()
    window.title('Main Window')
    window.configure(bg='black')

    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    window.geometry("%dx%d+0+0" % (w, h))

    voice_assistant_widget = VoiceAssistantWidget(window)
    voice_assistant_widget.show_wave = True
    voice_assistant_widget.show_wave_widget()

    HOME_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    import json
    from multiprocessing import Process, Queue
    with open(f'{HOME_DIR}{os.sep}widgets.json', encoding='utf-8') as widgets_config_file:
        WIDGETS_CONFIG = json.load(widgets_config_file)

    queue = Queue()
    assistant = VoiceAssistant(WIDGETS_CONFIG, queue)
    assistant_process = Process(target=assistant.listen).start()

    window.mainloop()
