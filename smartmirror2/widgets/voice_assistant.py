#!usr/bin/python3
# voice_assistant.py - voice assistant for my Smart Mirror project.

import logging
import speech_recognition as sr
from tkinter import *
import os
import time


class VoiceAssistant():
    
    def __init__(
        self,
        window,
        WIDGETS_CONFIG,
        relx=0.2, 
        rely=0.4, 
        width=0.4, 
        height=0.1, 
        anchor='nw'        
    ):
    
        self.logger = logging.getLogger('SM.voice_assistant')
        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)
        #self.logger.critical(f'{relx}, {rely}, {width}, {height}, {anchor}')
        self.window = window
        # Dimesnsions of the main window (screen size)
        self.window_width = window.winfo_screenwidth()
        self.window_height = window.winfo_screenheight()
        self.relx = relx
        self.rely = rely
        self.target_width = int(width * self.window_width)
        self.target_height = int(height * self.window_height)
        self.anchor = anchor

        self.assistant_frame = Frame(self.window, bg='black', bd=2)
        self.assistant_frame.place(relx=self.relx, rely=self.rely)

        self.frames = [PhotoImage(file=f'images{os.sep}wave.gif',format = 'gif -index %i' %(i)) for i in range(1,40)]
        self.wave_label = Label(self.assistant_frame, image=self.frames[0], bg='black', bd=0)
        self.wave_label.grid(column=1, row=0, sticky='nw')

        self.test_message = 'In the town where I was born lived a man who sailed to sea'
        self.message_label_target_width = self.target_width - self.frames[0].width()
        self.font_size = 12
        self.message = 'ГОВОРИТЕ: '
        self.message_label = Message(
            self.assistant_frame, text=self.test_message, 
            #width=self.message_label_target_width,
            fg='lightblue', bg='black', 
            font=("SFUIText", self.font_size, "bold")
        )
        self.message_label.grid(column=2, row=0, sticky=self.anchor)

        self.speech_recognizer = sr.Recognizer()

        #print(sr.Microphone.list_microphone_names())

        self.cmd = {}
        for key in WIDGETS_CONFIG.keys():
            self.cmd[WIDGETS_CONFIG[key]['name']] = WIDGETS_CONFIG[key]['show']
        #print(self.cmd)
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

        self.show = True
        self.show_wave = False
        self.logger.info('Voice assistant has been initialized!')
        self.voice_being_processed = False
        self.status()

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
            if self.show_wave:
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


    def listen(self, queue):
        self.voice_being_processed = True
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
                self._recognize(audio, queue)
            # Catches the exception when there is nothing said during speech recognition.
            except sr.WaitTimeoutError:
                self.logger.debug('Timeout: no speech has been registred.')
                self.voice_being_processed = False
                self.show_wave = False
                return None
            except Exception as exc:
                self.logger.debug(f'Cannot get the mic: {exc}')
                self.voice_being_processed = False
                self.show_wave = False
                return None

    def _recognize(self, audio, queue):
        try:
            user_speech = self.speech_recognizer.recognize_google(audio, language = "en-EN").lower()
            self.logger.debug(f'User said: {user_speech}')
            self.message_label.config(text=user_speech)
            time.sleep(2)
            self.message_label.config(text='')
            self.cmd_handler(user_speech, queue)
        except sr.UnknownValueError:
            self.logger.info('Cannot recognize speech...')
            self.voice_being_processed = False
            self.show_wave = False
            return None

            
    def cmd_handler(self, cmd, queue):
        """ Gets a string of recognized speech as cmd. 
            Checks if there are any sort of commands in it.
            Modifies self.cmd according to the detected commands."""

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

            self.logger.debug('All the widgets have been concealed!')

        elif self.second_part_command(cmd) and \
            (
            cmd.find('все виджеты') != -1 or \
            cmd.find('all the widgets') != -1 or \
            cmd.find('всю графику') != -1 or \
            cmd.find('всё') != -1
            ):

            (
            self.cmd['clock'], 
            self.cmd['spartak'], 
            self.cmd['marquee'],
            self.cmd['stocks'], 
            self.cmd['weather'],
            self.cmd['covid']
            ) = True, True, True, True, True, True
            self.cmd['youtube'].add('playback resume')
            self.logger.debug('All the widgets is being showing!')

        elif cmd.find('volume control') != -1:
            try:
                self.cmd['volume'] = int(cmd[cmd.rfind(' ') + 1:])
                self.cmd['volumeControl'] = True
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
            self.cmd['youtube'].add('fullscreen')
        
        elif cmd.find('убрать') != -1 or \
             cmd.find('окно') != -1 or \
             cmd.find('в угол') != -1 or \
             cmd.find('свернуть') != -1 or \
             cmd.find('window') != -1:
            self.cmd['youtube'].add('window')
            
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
            self.cmd['youtube'].add('playback stop')
        
        elif (
            cmd.find('видео') != -1 or \
            cmd.find('video') != -1 or \
            cmd.find('playback') != -1
            ) and \
            (
            cmd.find('пауза') != -1 or \
            cmd.find('pause') != -1
            ):
            self.cmd['youtube'].add('playback pause')
        
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
            self.cmd['youtube'].add('playback resume')
        
        # Youtube video search condition, for instance 'watch youtube Metallica', 
        # 'show video Liverpool Manchester City' 
        elif self.second_part_command(cmd) and \
            (
            cmd.find('youtube') != -1 or \
            cmd.find('video') != -1 or \
            cmd.find('видео') != -1 or \
            cmd.find('ютюб') != -1
            ):
            for c in self.show_commands:
                if cmd.find(c) != -1:
                    cmd = cmd[cmd.find(cmd):]
                    cmd = cmd.replace(c, '')
            self.cmd['youtube'].add(f'video search {cmd}')

        elif cmd.find('gestures') != -1 and \
             cmd.find('recognition') != -1 and \
             cmd.find('mode') != -1:
            self.cmd['gesturesMode'] = True

        elif cmd.find('gestures') != -1 and \
             cmd.find('recognition') != -1 and \
             cmd.find('mode') != -1 and \
             cmd.find('off') != -1:
            self.cmd['gesturesMode'] = False

        if len(self.cmd) > 0:
            self.logger.debug(f'The following phrases have been detected: {self.cmd}')
        queue.put({'detected_voice_command' : self.cmd})
        self.voice_being_processed = False
        self.show_wave = False
          
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
    window = Tk()
    window.title('Main Window')
    window.configure(bg='black')
    #window.overrideredirect(True)
    w, h = window.winfo_screenwidth(), window.winfo_screenheight()
    window.geometry("%dx%d+0+0" % (w, h))
    HOME_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    import json
    from multiprocessing import Process, Queue
    with open(f'{HOME_DIR}{os.sep}widgets.json', encoding='utf-8') as widgets_config_file:
        WIDGETS_CONFIG = json.load(widgets_config_file)
    assistant = VoiceAssistant(window, WIDGETS_CONFIG)
    #listen_thread = threading.Thread(target=assistant._listen).start()
    queue = Queue()
    assistant.show_wave = True
    assistant.show_wave_widget()
    assistant_process = Process(target=assistant.listen, args=(queue,)).start()
    window.mainloop()

