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

        if os.environ.get('DISPLAY', '') == '':
            os.environ.__setitem__('DISPLAY', ':0.0')

        self.speech_recognizer = sr.Recognizer()

        #print(sr.Microphone.list_microphone_names())

        self.queue = queue

        self.cmd = {}

        self.WIDGETS_CONFIG = WIDGETS_CONFIG

        for key in self.WIDGETS_CONFIG.keys():
            self.cmd[self.WIDGETS_CONFIG[key]['name']] = self.WIDGETS_CONFIG[key]['show']

        self.cmd['update'] = False
        self.cmd['youtube_search'] = False
        self.cmd['youtube_stop'] = False
        self.cmd['youtube_pause'] = False
        self.cmd['youtube_play'] = False
        self.cmd['youtube_volume'] = False
        self.cmd['youtube_fullscreen'] = False
        self.cmd['youtube_window'] = False

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
        )

        self.video_commands = (
            'youtube',
            'video',
            'видео',
            'ютюб',
            'ютуб'
        )

        self.all_widgets_commands = (
            'все виджеты',
            'всю графику',
            'всё',
            'all the widgets',
            'all widgets'
        )

        self.fullscreen_commands = (
            'развернуть',
            'весь экран',
            'полный экран',
            'полноэкранный',
            'full screen',
            'fullscreen'
        )

        self.window_commands = (
             'окно',
             'свернуть',
             'оконный',
             'window',
        )

        self.video_stop_commands = (
            'стоп',
            'остановить',
            'stop'
        )

        self.video_pause_commands = (
            'пауза',
            'pause'
        )

        self.video_play_commands = (
            'возобновить',
            'продолжить',
            'resume',
            'play'
        )

        self.video_search_commands = (
            'смотреть',
            'найти',
            'искать',
            'воспроизвести',
            'play',
            'search',
            'find',
            'watch'
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
                audio = self.speech_recognizer.listen(source, timeout=4, phrase_time_limit=3)
                
                #self.message_label.config(text='CONFIG')
                self._recognize(audio)
            # Catches the exception when there is nothing said during speech recognition.
            except sr.WaitTimeoutError:
                self.logger.debug('Timeout: no speech has been registred.')
                self.queue.put({'voice_assistant' : {'error': True}})
            except Exception as exc:
                self.logger.error(f'Cannot get the mic: {exc}')
                self.queue.put({'voice_assistant' : {'error': True}})

    def _recognize(self, audio):
        self.logger.info('Trying to recognize speech...')
        try:
            user_speech = self.speech_recognizer.recognize_google(audio, language = "ru-RU").lower()
            self.logger.debug(f'User said: {user_speech}')
            self.cmd_handler(user_speech)
        except Exception as exc:
            self.logger.error(f'Cannot recognize speech: {exc}')
            self.queue.put({'voice_assistant' : {'error': True}})
            
    def cmd_handler(self, phrase):
        """ Gets a string of recognized speech as cmd. 
            Checks if there are any sort of commands in it.
            Modifies self.cmd according to the detected commands."""

        self.logger.info('Looking for commands in the speech...')

        words_to_exclude = set()

        detected_words = {
            'all_widgets': False, 
            'show': False,
            'hide': False,
            'clock': False,
            'calendar': False,
            'weather': False,
            'stocks': False,
            'covid': False,
            'ticker': False,
            'spartak': False,
            'volume': False,
            'video': False,
            'fullscreen': False,
            'window': False,
            'stop': False,
            'pause': False,
            'play': False,
            'search': False
        }

        for command in self.video_commands:
            if phrase.find(command) != -1:
                words_to_exclude.add(command)
                detected_words['video'] = True

        for command in self.video_search_commands:
            if phrase.find(command) != -1:
                words_to_exclude.add(command)
                detected_words['search'] = True

        # If there is a phrase assosiated with video search:
        if detected_words['search'] and detected_words['video']:
            self.logger.debug('Video SEARCH command detected!')
            for word in words_to_exclude:
                if phrase.find(word) != -1:
                    phrase= phrase.replace(word, '')
            phrase = phrase.strip()
            self.cmd['youtube_search'] = phrase
            self.cmd['update'] = True

        if phrase.find('громкость') != -1:
            words_to_exclude.add('громкость')
            detected_words['volume'] = True

        if detected_words['volume'] and detected_words['video']:
            self.logger.debug('Video VOLUME command detected!')
            self.cmd['youtube_volume'] = True
            self.cmd['update'] = True

        for command in self.fullscreen_commands:
            if phrase.find(command) != -1:
                words_to_exclude.add(command)
                detected_words['fullscreen'] = True

        if detected_words['fullscreen'] and detected_words['video']:
            self.logger.debug('Video FULLSCREEN command detected!')
            self.cmd['youtube_fullscreen'] = True
            self.cmd['update'] = True

        for command in self.window_commands:
            if phrase.find(command) != -1:
                words_to_exclude.add(command)
                detected_words['window'] = True
        
        if detected_words['window'] and detected_words['video']:
            self.logger.debug('Video WINDOW MODE command detected!')
            self.cmd['youtube_window'] = True
            self.cmd['update'] = True

        for command in self.video_stop_commands:
            if phrase.find(command) != -1:
                words_to_exclude.add(command)
                detected_words['stop'] = True

        if detected_words['stop'] and detected_words['video']:
            self.logger.debug('Video STOP command detected!')
            self.cmd['youtube_stop'] = True
            self.cmd['update'] = True

        for command in self.video_pause_commands:
            if phrase.find(command) != -1:
                words_to_exclude.add(command)
                detected_words['pause'] = True

        if detected_words['pause'] and detected_words['video']:
            self.logger.debug('Video PAUSE command detected!')
            self.cmd['youtube_pause'] = True
            self.cmd['update'] = True

        for command in self.video_play_commands:
            if phrase.find(command) != -1:
                words_to_exclude,add(command)
                detected_words['play'] = True

        if detected_words['play'] and detected_words['video']:
            self.logger.debug('Video PLAY command detected!')
            self.cmd['youtube_play'] = True
            self.cmd['update'] = True


        for command in self.all_widgets_commands:
            if phrase.find(command) != -1:
                words_to_exclude.add(command)
                detected_words['all_widgets'] = True

        for command in self.show_commands:
            if phrase.find(command) != -1:
                words_to_exclude.add(command)
                detected_words['show'] = True

        if detected_words['all_widgets'] and detected_words['show']:
            for widget in self.WIDGETS_CONFIG.keys():
                self.cmd[widget] = True
            self.cmd['update'] = True
            self.logger.debug('SHOW all the widgets command detected!')

        for command in self.hide_commands:
            if phrase.find(command) != -1:
                words_to_exclude.add(command)
                detected_words['hide'] = True

        if detected_words['all_widgets'] and detected_words['hide']:
            for widget in self.WIDGETS_CONFIG.keys():
                self.cmd[widget] = False
            self.cmd['update'] = True
            self.logger.debug('HIDE all the widgets command detected!')

        if phrase.find('часы') != -1 or phrase.find('clock') != -1:
            words_to_exclude.add('часы')
            words_to_exclude.add('clock')
            if detected_words['show']:
                self.cmd['clock'] = True
                self.cmd['update'] = True
                self.logger.debug('CLOCK widget SHOW command detected!')
            elif detected_words['hide']:
                self.logger.debug('CLOCK widget HIDE command detected!')
                self.cmd['clock'] = False
                self.cmd['update'] = True

        if phrase.find('календарь') != -1 or phrase.find('calendar') != -1:
            words_to_exclude.add('календарь')
            words_to_exclude.add('calendar')
            if detected_words['show']:
                self.logger.debug('CALENDAR widget SHOW command detected!')
                self.cmd['calendar'] = True
                self.cmd['update'] = True
            elif detected_words['hide']:
                self.logger.debug('CALENDAR widget HIDE command detected!')
                self.cmd['calendar'] = False
                self.cmd['update'] = True

        if phrase.find('погода') != -1 or phrase.find('weather') != -1:
            words_to_exclude.add('погода')
            words_to_exclude.add('weather')
            if detected_words['show']:
                self.logger.debug('WEATHER widget SHOW command detected!')
                self.cmd['weather'] = True
                self.cmd['update'] = True
            elif detected_words['hide']:
                self.logger.debug('WEATHER widget HIDE command detected!')
                self.cmd['weather'] = False
                self.cmd['update'] = True

        if phrase.find('курсы') != -1 or phrase.find('курс') != -1 or phrase.find('stocks') != -1:
            words_to_exclude.add('курсы')
            words_to_exclude.add('курс')
            words_to_exclude.add('stocks')
            if detected_words['show']:
                self.logger.debug('STOCKS widget SHOW command detected!')
                self.cmd['stocks'] = True
                self.cmd['update'] = True
            elif detected_words['hide']:
                self.logger.debug('STOCKS widget HIDE command detected!')
                self.cmd['stocks'] = False
                self.cmd['update'] = True

        if phrase.find('коронавирус') != -1 or phrase.find('ковид') != -1 or phrase.find('covid') != -1 or phrase.find('coronavirus') != -1:
            words_to_exclude.add('коронавирус')
            words_to_exclude.add('ковид')
            words_to_exclude.add('covid')
            words_to_exclude.add('coronavirus')
            if detected_words['show']:
                self.logger.debug('COVID widget SHOW command detected!')
                self.cmd['covid'] = True
                self.cmd['update'] = True
            elif detected_words['hide']:
                self.logger.debug('COVID widget HIDE command detected!')
                self.cmd['covid'] = False
                self.cmd['update'] = True

        if phrase.find('спартак') != -1 or phrase.find('spartak') != -1:
            words_to_exclude.add('spartak')
            words_to_exclude.add('спартак')
            if detected_words['show']:
                self.logger.debug('SPARTAK widget SHOW command detected!')
                self.cmd['spartak'] = True
                self.cmd['update'] = True
            elif detected_words['hide']:
                self.logger.debug('SPARTAK widget HIDE command detected!')
                self.cmd['spartak'] = False
                self.cmd['update'] = True

        if phrase.find('строка') != -1 or phrase.find('строку') != -1 or phrase.find('ticker') != -1:
            words_to_exclude.add('строка')
            words_to_exclude.add('строку')
            if detected_words['show']:
                self.logger.debug('TICKER widget SHOW command detected!')
                self.cmd['ticker'] = True
                self.cmd['update'] = True
            elif detected_words['hide']:
                self.logger.debug('TICKER widget HIDE command detected!')
                self.cmd['ticker'] = False
                self.cmd['update'] = True

        if self.cmd['update']:
            self.logger.debug(f'The following commands will be processed: {self.cmd}')
            cmd = self.cmd.copy()
            # Have to make a copy of the commands in order to leave them intouch
            # while processing by the main module.
            self.queue.put({'voice_assistant' : cmd})

        else:
            self.queue.put({'voice_assistant': {'update': False}})
            self.logger.debug('No commands have been found in the speech!')

        self.cmd['update'] = False
        self.cmd['youtube_search'] = False
        self.cmd['youtube_stop'] = False
        self.cmd['youtube_pause'] = False
        self.cmd['youtube_play'] = False
        self.cmd['youtube_volume'] = False
        self.cmd['youtube_fullscreen'] = False
        self.cmd['youtube_window'] = False

        if __name__ == '__main__':
            next_listening_cycle = Process(target=self.listen).start()
          
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
