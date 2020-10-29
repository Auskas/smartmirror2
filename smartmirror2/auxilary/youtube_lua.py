#!/usr/bin/python3
# youtube_lua.py
#
# The script downloads the 'youtube.lua' file that is used for playing Youtube videos over VLC player.
# It also overwrites the existing file with the freshly downloaded one.
# The script tries to determine the location of the system 'youtube.lua file'.
# Windows users! Make sure to run the script under the administrator rights.

import os, sys, platform
import shutil
import time
import requests
import logging
import subprocess

class LuaUpdater:

    def __init__(self):
        # The module is part of my SmartMirror project, therefore the following logging convention is used.
        self.logger = logging.getLogger('SM.youtube_lua')

        self.UPDATE_INTERVAL = 3600

        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)

        self.user_system = platform.system()

        if self.user_system == 'Linux':
            if os.geteuid() == 0:
                self.logger.debug('Script is running under root privileges.')
                self.is_root = True
            else:
                self.logger.debug('Script is not running under root privileges.')
                self.is_root = False
            process = subprocess.Popen('locate youtube.luac', stdout=subprocess.PIPE, shell=True)
            self.target_file = process.communicate()[0].strip().decode('utf-8')
            if self.target_file == '':
                self.logger.error('Cannot locate the target file in your Linux system.')
            else:
                self.logger.debug(f'Target file path: {self.target_file}')

        elif self.user_system == 'Windows':
            target_file_32_bit = f'C:{os.sep}Program Files (x86){os.sep}VideoLAN{os.sep}VLC{os.sep}lua{os.sep}playlist{os.sep}youtube.luac'
            target_file_64_bit = f'C:{os.sep}Program Files{os.sep}VideoLAN{os.sep}VLC{os.sep}lua{os.sep}playlist{os.sep}youtube.luac'
            if os.path.isfile(target_file_32_bit):
                self.logger.debug(f'Target file has been detected (32 bit OS): {target_file_32_bit}')
                self.target_file = target_file_32_bit
            elif os.path.isfile(target_file_64_bit):
                self.logger.debug(f'Target file has been detected (64 bit OS): {target_file_64_bit}')
                self.target_file = target_file_64_bit
            else:
                self.logger.error('Cannot locate the lua file in windows.')
                self.target_file = ''

        else:
            self.logger.warning('Sorry your OS is not supported!')

        # The source URL where the lua file is located. The community periodically updates 
        # the file responding to changes in Youtube algorithms.
        self.url = 'https://raw.githubusercontent.com/videolan/vlc/master/share/lua/playlist/youtube.lua'
        
        # The path to a temp file prior to copying it to the destination.
        # As default the script saves the temp file into the current working directory.
        self.temp_file = f'{os.getcwd()}{os.sep}youtube.lua'
        self.logger.debug(f'Temp file path: {self.temp_file}')

    def get_page(self, link):
        """ Loads a web page using 'requests' module. 
            Returns the result as text if the status is OK.
            Otherwise, returns False.
            Arguments: link as a string."""
        try:
            res = requests.get(link)
        except Exception as error:
            self.logger.error(f'Cannot load the page, the following error occured: {error}')
            return False
        try:
            res.raise_for_status()
            self.logger.debug('Page {0} has been successfully loaded.'.format(link))
            return res.text
        except Exception as error:
            self.logger.error('Cannot get the page {0}'.format(link))
            self.logger.error('The following error occured: {0}'.format(error))
            return False

    def updater(self):
        """ The method downloads the youtube.lua file from self.url (github videolan repository).
            The method does not check the version of the file.

            If the module is executed under root privileges, the newly obtained data is written directly to the destination file.
            Otherwise, a subprocess is called to copy the file."""
        luac = self.get_page(self.url)

        if luac:

            if self.user_system == 'Linux':
                if self.is_root:
                    with open(self.target_file, 'w') as target_file:
                        target_file.write(luac)
                    self.logger.debug('youtube.luac has been successfully updated.')
                else:
                    with open(self.temp_file, 'w') as temp_file:
                        temp_file.write(luac)
                    self.logger.debug('youtube.luac has been saved to a temp file.')
                    try:
                        subprocess.call(['sudo', 'cp', '-rf', self.temp_file, self.target_file])
                        self.logger.debug('youtube.luac has been successfully updated.')
                    except Exception as error:
                        self.logger.debug(f'Cannot rewrite the file: {error}')

            elif self.user_system == 'Windows':
                if self.target_file != '':
                    with open(self.temp_file, 'w') as temp_file:
                        temp_file.write(luac)
                    self.logger.debug('youtube.luac has been saved to a temp file.')
                    try:
                        shutil.copy(self.temp_file, self.target_file)
                    except Exception as copy_error:
                        self.logger.error(f'Cannot copy the file: {copy_error}')

            # If the OS is neither Linux nor Windows, then it is probably OS X.
            # The chunk of such code is not ready. In fact, I am not familiar with MacOS.
            else:
                pass

            try:
                #os.remove(self.temp_file)
                self.logger.debug('Temp file has been deleted.')
            except Exception as remove_error:
                self.logger.error(f'Cannot delete the temp file: {remove_error}')

    def schedule(self):
        while True:
            self.updater()
            time.sleep(self.UPDATE_INTERVAL)

if __name__ == '__main__':
    updater = LuaUpdater()
    updater.updater()
