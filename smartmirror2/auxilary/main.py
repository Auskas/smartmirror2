#!/usr/bin/env python3
# main.py - client for Gesell Smart Mirror

import threading
import socket
import subprocess
import re
import os
import time
import json
import logging
import Crypto
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
from Crypto import Random

import kivy
from kivy.core.window import Window
from kivy.app import App
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.textinput import TextInput 
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.slider import Slider
kivy.require('1.10.1')
print(f'Kivy version {kivy.__version__}')

class ManagementPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        FONT_SIZE = 18
        self.RED = [1, 0, 0, 1]
        self.GREEN = [0, 1, 0, 1]

        self.volume = 0
        self.volume_change_sent = True

        self.controls_grid = GridLayout(cols=2)

        self.clock_button = Button(font_size=FONT_SIZE, text='Clock ON/OFF')
        self.clock_button.bind(on_press=self.clock_switch)
        self.controls_grid.add_widget(self.clock_button)
        self.stocks_button = Button(font_size=FONT_SIZE, text='Stocks ON/OFF')
        self.stocks_button.bind(on_press=self.stocks_switch)
        self.controls_grid.add_widget(self.stocks_button)

        self.weather_button = Button(font_size=FONT_SIZE, text='Weather ON/OFF')
        self.weather_button.bind(on_press=self.weather_switch)
        self.controls_grid.add_widget(self.weather_button)
        self.covid_button = Button(font_size=FONT_SIZE, text='Covid ON/OFF')
        self.covid_button.bind(on_press=self.covid_switch)
        self.controls_grid.add_widget(self.covid_button)

        self.ticker_button = Button(font_size=FONT_SIZE, text='Ticker ON/OFF')
        self.ticker_button.bind(on_press=self.ticker_switch)
        self.controls_grid.add_widget(self.ticker_button)
        self.spartak_button = Button(font_size=FONT_SIZE, text='Spartak ON/OFF')
        self.spartak_button.bind(on_press=self.spartak_switch)
        self.controls_grid.add_widget(self.spartak_button)

        self.add_widget(self.controls_grid)

        self.youtube_controls_grid = GridLayout(cols=4)
        self.play_button = Button(text='',
                                  background_normal = f'.{os.sep}icons{os.sep}play_icon.png', 
                                  background_down = f'.{os.sep}icons{os.sep}stop_icon.png')
        self.add_widget(self.youtube_controls_grid)
        self.youtube_controls_grid.add_widget(self.play_button)

        self.youtube_search_grid = GridLayout(cols=2)
        self.add_widget(self.youtube_search_grid)

        self.youtube_search = TextInput(multiline=False)
        self.youtube_search_grid.add_widget(self.youtube_search)

        self.submit = Button(font_size=FONT_SIZE, text='Search Youtube')
        self.submit.bind(on_press=self.youtube_search_submit)
        self.youtube_search_grid.add_widget(self.submit)

        self.slider = Slider(min=0, 
                             max=100, 
                             value=self.volume, 
                             value_track = True, 
                             value_track_color =[1, 0, 0, 1]
                             )
        self.slider.bind(value=self.slider_volume_change)
        self.add_widget(self.slider)

    def slider_volume_change(self, instance, volume):
        self.volume = volume
        self.volume_change_sent = False

    def volume_updater(self):
        """ Checks every second if there is a need to send a volume update."""
        while True:
            time.sleep(1)
            if self.volume_change_sent == False:
                message = f'volume control {str(int(self.volume))}'
                try:
                    backend.s.sendall(backend.encryption(message))
                    self.volume_change_sent = True
                except Exception as sending_error:
                    logger.error(f'Cannot send a volume update message: {sending_error}')
                    self.initial_page.update_info('Connection lost!')
                    backend.s.close()
                    time.sleep(2)
                    self.screen_manager.current = 'Reconnect'

    def youtube_search_submit(self, instance):
        message = f'watch video {self.youtube_search.text}'
        print(message)
        backend.s.sendall(backend.encryption(message))

    def clock_switch(self, instance):
        if backend.capabilities['clock']:
            backend.s.sendall(backend.encryption('hide clock'))
            self.clock_button.background_color = self.RED
        else:
            backend.s.sendall(backend.encryption('show clock'))
            self.clock_button.background_color = self.GREEN           

    def stocks_switch(self, instance):
        if backend.capabilities['stocks']:
            backend.s.sendall(backend.encryption('hide stocks'))
            self.stocks_button.background_color = self.RED
        else:
            self.stocks_button.background_color = self.GREEN
            backend.s.sendall(backend.encryption('show stocks'))  

    def weather_switch(self, instance):
        if backend.capabilities['weather']:
            backend.s.sendall(backend.encryption('hide weather'))
            self.weather_button.background_color = self.RED
        else:
            backend.s.sendall(backend.encryption('show weather'))
            self.weather_button.background_color = self.GREEN

    def covid_switch(self, instance):
        if backend.capabilities['covid']:
            backend.s.sendall(backend.encryption('hide covid'))
            self.covid_button.background_color = self.RED
        else:
            backend.s.sendall(backend.encryption('show covid'))
            self.covid_button.background_color = self.GREEN

    def ticker_switch(self, instance):
        if backend.capabilities['marquee']:
            backend.s.sendall(backend.encryption('hide ticker'))
            self.ticker_button.background_color = self.RED
        else:
            backend.s.sendall(backend.encryption('show ticker'))
            self.ticker_button.background_color = self.GREEN

    def spartak_switch(self, instance):
        if backend.capabilities['spartak']:
            backend.s.sendall(backend.encryption('hide spartak'))
            self.spartak_button.background_color = self.RED
        else:
            backend.s.sendall(backend.encryption('show spartak'))
            self.spartak_button.background_color = self.GREEN

class ReconnectPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        FONT_SIZE = 18
        self.reconnect_button = Button(font_size=FONT_SIZE, text='Reconnect')
        self.reconnect_button.bind(on_press=self.reconnect)
        self.add_widget(self.reconnect_button)

    def reconnect(self, instance):
        reconnectThread = threading.Thread(target=backend.ip_address_discovery)
        reconnectThread.start()

class CredentialsPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.add_widget(Label(font_size=18, text='Enter your credentials'))

        self.bottom_widget = GridLayout(cols=2)
        self.password_text_input = TextInput(multiline=False, 
                                             hint_text='Enter the passcode here',
                                             password=True
                                             )
        self.submit_password_button = Button(text='Submit')
        self.submit_password_button.bind(on_press=self.submit_password)
        self.bottom_widget.add_widget(self.password_text_input)
        self.bottom_widget.add_widget(self.submit_password_button)

        self.add_widget(self.bottom_widget)

    def submit_password(self, instance):
        submitThread = threading.Thread(target=backend.send_password)
        submitThread.start()

class InitialPage(GridLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.cols = 1
        self.text_label = Label(halign='center', valign='middle',
                                font_size=18, text='')
        #self.text_label.bind(width=self.update_text_width)
        self.add_widget(self.text_label)

    def update_info(self, message):
        self.text_label.text = message

    def update_text_width(self):
        self.text_label.text_size = (self.text_label.width * 0.9, None)

class ClientApp(App):
    def build(self):

        self.screen_manager = ScreenManager()

        self.initial_page = InitialPage()
        screen = Screen(name='Initial')
        screen.add_widget(self.initial_page)
        self.screen_manager.add_widget(screen)

        self.credentials_page = CredentialsPage()
        screen = Screen(name='Credentials')
        screen.add_widget(self.credentials_page)
        self.screen_manager.add_widget(screen)

        self.management_page = ManagementPage()
        screen = Screen(name='Management')
        screen.add_widget(self.management_page)
        self.screen_manager.add_widget(screen)

        self.reconnect_page = ReconnectPage()
        screen = Screen(name='Reconnect')
        screen.add_widget(self.reconnect_page)
        self.screen_manager.add_widget(screen)

        return self.screen_manager

class Backend:

    def __init__(self):
        self.is_password_checked = False
        self.ip_address_discovered = None
        self.capabilities = None
        #self.PING_COMMAND = 'ping gesell.local -c 3'
        self.PING_COMMAND = 'ping auskas-ubuntu.local -c 3'
        self.PORT = 1175        # The port used by the server
        self.RED = [1, 0, 0, 1]
        self.GREEN = [0, 1, 0, 1]

        random_generator = Random.new().read
        self.key = RSA.generate(2048, random_generator)
        self.public_key = self.key.publickey().exportKey()
        self.cipher_client_private = PKCS1_v1_5.new(self.key)
        #print(type(socket.gethostbyname('auskas-ubuntu.local')))

    def ip_address_discovery(self):
        #process = subprocess.Popen(self.PING_COMMAND, stdout=subprocess.PIPE, shell=True)
        #stdout = process.communicate()[0].strip()
        #ip_address_regex = re.compile(r'\d+.\d+.\d+.\d+')
        #ip_address = ip_address_regex.search(stdout.decode('utf-8'))
        time.sleep(1)
        print('Setting the initial page...')
        clientApp.screen_manager.current = 'Initial'
        clientApp.initial_page.update_info('Discovering the server...')
        time.sleep(1)
        #logger.info(f'HOSTNAME: {socket.gethostname()}')
        logger.info('Trying to locate the server...')

        PORT = 7511
        SYNCHRO_WORD = 'gesell2020 @' 
        broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) #create UDP socket
        broadcast_socket.bind(('', PORT))

        while True:
            data, addr = broadcast_socket.recvfrom(1024) #wait for a packet
            data = data.decode()
            print(data)
            if data.startswith(SYNCHRO_WORD):
                try:
                    self.HOST = data[data.find('@') + 1:]
                    break
                except Exception as error:
                    print(f'Something went wrong, cannot get the IP address: {error}')
        try:
            self.ip_address_discovered = True
            print(f'Server has been discovered: IP address {self.HOST}')
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                self.s.connect((self.HOST, self.PORT))
                clientApp.initial_page.update_info('Connected to the server!')
                time.sleep(2)
                print('Connected to the server')
                self.server_public_key = self.crypto_keys_exchange()
                if self.server_public_key == False:
                    clientApp.initial_page.update_info('Cannot get server\'s public RSA key.')
                    self.s.close()
                    time.sleep(2)
                    clientApp.screen_manager.current = 'Reconnect'
                else:
                    clientApp.initial_page.update_info('Got server\'s public RSA key.')

                    time.sleep(2)
                    # Displays the password input screen.
                    clientApp.screen_manager.current = 'Credentials'
            except Exception as error:
                clientApp.initial_page.update_info('Server does not respond!')
                self.s.close()
                time.sleep(2)
                clientApp.screen_manager.current = 'Reconnect'
        except Exception as error:
            logger.debug(f'Error: {error}')
            self.HOST = None
            self.ip_address_discovered = False
            print('Cannot find the server IP address. Terminating the program...')
            clientApp.initial_page.update_info('Cannot discover the server!')
            time.sleep(2)
            clientApp.screen_manager.current = 'Reconnect'

    def crypto_keys_exchange(self):
        while True:
            try:
                data = self.s.recv(1024)
                data = data.decode()
                print(data)
                if data.find('-----END PUBLIC KEY-----') != -1 and \
                   data.find('-----BEGIN PUBLIC KEY-----') != -1:
                   self.s.sendall(self.public_key)
                   print('Got the server\'s public RSA key')
                   self.cipher_server_public = PKCS1_v1_5.new(RSA.importKey(data))
                   return data
                else:
                    print('Cannot get the key')
                    return False
                if not data:
                    break
            except Exception as exc:
                print('Connection lost!')
        return False

    def encryption(self, message):
        message = message.encode('utf-8')
        try:
            encrypted_message = self.cipher_server_public.encrypt(message)
            return encrypted_message
        except ValueError:
            print('Message too long')

        

    def send_password(self):
        logger.debug('Sending the password to the server...')
        password_user = clientApp.credentials_page.password_text_input.text
        password_user_bytes = password_user.encode('utf-8')
        self.s.sendall(self.encryption(password_user))
        while True:
            data = self.s.recv(1024)
            if not data:
                logger.error('Connection to the server has been lost!')
                clientApp.initial_page.update_info('Connection lost!')
                clientApp.screen_manager.current = 'Initial'
                self.s.close()
                time.sleep(2)
                clientApp.screen_manager.current = 'Reconnect'
                break                
            data = self.cipher_client_private.decrypt(data, Random.new().read)
            data = data.decode()
            logger.debug(f'Server response: {data}')
            if data == 'Connection refused':
                print('Server has terminated the connection')
                clientApp.screen_manager.current = 'Initial'
                clientApp.initial_page.update_info('Wrong credentials!')
                time.sleep(2)
                self.s.close()
                clientApp.screen_manager.current = 'Reconnect'
                break
            elif data.find('Access granted') != -1:
                self.is_password_checked = True
                data = data[data.find('{'):]
                print(data)
                self.capabilities = json.loads(data)
                clientApp.screen_manager.current = 'Initial'
                clientApp.initial_page.update_info('You have successfully logged in!')
                time.sleep(2)
                clientApp.screen_manager.current = 'Management'
                clientApp.management_page.slider.value = self.capabilities['volume']
                clientApp.management_page.volume = self.capabilities['volume']

                # The following thread is used to send the volume changes.
                volumeUpdaterThread = threading.Thread(target=clientApp.management_page.volume_updater)
                volumeUpdaterThread.start()

                self.initial_color()
                self.update()
                break

    def initial_color(self):
        if self.capabilities['clock']:
            clientApp.management_page.clock_button.background_color = self.GREEN
        else:
            clientApp.management_page.clock_button.background_color = self.RED

        if self.capabilities['stocks']:
            clientApp.management_page.stocks_button.background_color = self.GREEN
        else:
            clientApp.management_page.stocks_button.background_color = self.RED

        if self.capabilities['weather']:
            clientApp.management_page.weather_button.background_color = self.GREEN
        else:
            clientApp.management_page.weather_button.background_color = self.RED

        if self.capabilities['covid']:
            clientApp.management_page.covid_button.background_color = self.GREEN
        else:
            clientApp.management_page.covid_button.background_color = self.RED

        if self.capabilities['marquee']:
            clientApp.management_page.ticker_button.background_color = self.GREEN
        else:
            clientApp.management_page.ticker_button.background_color = self.RED

        if self.capabilities['spartak']:
            clientApp.management_page.spartak_button.background_color = self.GREEN
        else:
            clientApp.management_page.spartak_button.background_color = self.RED

    def update(self):
        while True:
            data = self.s.recv(4096)
            if not data:
                logger.error('Connection to the server has been lost!')
                clientApp.initial_page.update_info('Connection lost!')
                clientApp.screen_manager.current = 'Initial'
                self.s.close()
                time.sleep(2)
                clientApp.screen_manager.current = 'Reconnect'
                break
            data = self.cipher_client_private.decrypt(data, Random.new().read)
            data = data.decode()
            if data == 'Connection refused':
                break
            elif data.find('Capabilities') != -1:
                try:
                    data = data[data.find('{'):data.find('}') + 1]
                    print(f'Get the JSON: {data}')
                    self.capabilities = json.loads(data)
                except Exception as error:
                    print(f'Cannot get the JSON: {error}')
                #clientApp.management_page.slider.value = self.capabilities['volume']
                #clientApp.screen_manager.current = 'Initial'
                #clientApp.initial_page.update_info('You have successfully logged in!')
                #time.sleep(2)
                #clientApp.screen_manager.current = 'Management'


if __name__ == '__main__':
    logger = logging.getLogger('Gesell')
    logger.setLevel(logging.DEBUG)
    logConsole = logging.StreamHandler()
    logConsole.setLevel(logging.DEBUG)
    formatterConsole = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    logConsole.setFormatter(formatterConsole)
    logger.addHandler(logConsole)
    logger.info('BEGIN OF THE SCRIPT')

    clientApp = ClientApp() 
    backend = Backend()
    backendThread = threading.Thread(target=backend.ip_address_discovery)
    backendThread.start()

    clientApp.run()