#!usr/bin/python3
# wifimanager.py - the module scans available wifi hotspots.

import subprocess
import re
import logging

logger = logging.getLogger('django.wifiscan')

def scanner(interface=False):
    """ Calls the iwlist terminal command to get its output.
        The keyword interface can be used to scan a particular interface.
        Otherwise, all the interfaces will be scanned.
        Returns the result as a string"""
    try:
        if interface:
            proc = subprocess.Popen(
                ["sudo", "iwlist", interface, "scan"], 
                stdout=subprocess.PIPE, 
                universal_newlines=True
            )
            proc2 = subprocess.Popen(
                ["sudo", "iwconfig"], 
                stdout=subprocess.PIPE, 
                universal_newlines=True
            )
        else:
            proc = subprocess.Popen(
                ["sudo", "iwlist", "scan"], 
                stdout=subprocess.PIPE, 
                universal_newlines=True
            )
            proc2 = subprocess.Popen(
                ["sudo", "iwconfig"], 
                stdout=subprocess.PIPE, 
                universal_newlines=True
            )
        output, error = proc.communicate()
        output2, error2 = proc2.communicate()
        return parser(output, output2)
    except Exception as exc:
        logger.exception('Cannot get the stdout of iwlist command: ')
        return False
    
def parser(result, result2, index=0):
    found_hotspots = {}
    lines = result.split('\n')
    cell_number_regex = re.compile(r'Cell \d\d - Address: \w\w:\w\w:\w\w:\w\w:\w\w:\w\w')
    quality_regex = re.compile(r'Quality=\d\d/\d\d')
    encryption_regex = re.compile(r'Encryption key:.*')
    SSID_regex = re.compile(r'ESSID:".*"')
    channel_regex = re.compile(r'Channel:.*')

    try:
        while index < len(lines):
            cell_number_string = cell_number_regex.search(lines[index])
            
            if cell_number_string is not None:
                cell_number = cell_number_string.group()[5:7]
                found_hotspots[cell_number] = {
                    'SSID': None,
                    'channel': None,
                    'quality': None,
                    'encryption': None
                }
                
                while index < len(lines):
                    quality_string = quality_regex.search(lines[index])
                    encryption_string = encryption_regex.search(lines[index])
                    SSID_string = SSID_regex.search(lines[index])
                    channel_string = channel_regex.search(lines[index])
                    
                    if channel_string is not None:
                        channel = channel_string.group()[8:len(channel_string.group())]
                        found_hotspots[cell_number]['channel'] = channel
                    
                    elif encryption_string is not None:
                        encryption = encryption_string.group()[15:len(encryption_string.group())]
                        if encryption == 'on':
                            encryption = True
                        elif encryption == 'off:':
                            encryption == False
                        else:
                            encryption = None
                        found_hotspots[cell_number]['encryption'] = encryption
                    
                    elif quality_string is not None:
                        quality = quality_string.group()[8:len(quality_string.group())]
                        try:
                            quality = str(int(eval(quality) * 100))
                        except Exception as exc:
                            quality = None
                        found_hotspots[cell_number]['quality'] = quality
                    elif SSID_string is not None:
                        SSID = SSID_string.group()[7:len(SSID_string.group()) - 1]
                        
                        found_hotspots[cell_number]['SSID'] = SSID
                        break
                    index += 1
            index += 1
        
        lines = result2.split('\n')
        connected_SSID = ''
        for line in lines:
            SSID_string = SSID_regex.search(line)
            if SSID_string is not None:
                connected_SSID = SSID_string.group()[7:len(SSID_string.group()) - 1]            
        return found_hotspots, connected_SSID
    except Exception as exc:
        logger.exception('Cannot parse the result of scan: ')
        return False

def connect(credentials):
    try:
        proc = subprocess.Popen(
            [
                "nmcli", 
                "dev", 
                "wifi", 
                "connect", 
                credentials['ssid'],
                "password",
                credentials['password']
            ], 
            stdout=subprocess.PIPE, 
            universal_newlines=True
        )
        output, error = proc.communicate()
        success_regex = re.compile(r"Device '.*' successfully activated with")
        if success_regex.search(output) is not None:
            return True
        else:
            return False
    except Exception as exc:
        logger.exception('Cannot connect to the hotspot')
        return False

if __name__ == '__main__':
    #result, result2 = scanner()
    #print(result)
    #print(result2)
    a = connect({"ssid": "iPhoneCovax", "password": "Python4ever"})
    print(a)