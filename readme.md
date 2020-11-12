# Smart Mirror Mark II

Smart Mirror Mark II is the second generation of my personal project.
Note: the main language is Russian.

## Available widgets:
- Clock;
- Calendar;
- Weather (based on Yandex Weather API);
- Stocks (exchange rates and oil prices);
- Youtube (based on Python VLC bindings);
- Ticker (a moving string of the latest news);
- COVID-19 (global and local Russian figures).

## Features:
- Gesture control. A web camera can be used to recognize static hand gestures in order to increase or decrease the audio volume of the playback. A CNN with a combination of background substraction is used to achieve the goal. An open palm is the gesture that initiates the voice control feature.
- Voice control. The main purpose of the voice control is to search videos on Youtube as well as to conceal and show the widgets. Youtube fullscreen mode is also activated via the voice control.
- Web interface. Based on Django, a user-friendly web interface can be used to move the widgets across the screen and resize them. There is a special page to choose and connect to a particular WiFi hotspot.

## Installation:
At the moment, installation is available from the repository:
```
$ git clone https://github.com/Auskas/smartmirror2.git
```

## Execution:
To run the script execute the following command:
```
$ python3 smartmirror2/smartmirror2/main.py
```
To run the web server execute the following command:
```
$ python3 smartmirror2/web/manage.py runserver
```
## Examples:
Smart mirror interface
![interface_example](https://github.com/Auskas/smartmirror2/blob/master/demo/demo1.gif)
Web interface
![web_interface_example](https://github.com/Auskas/smartmirror2/blob/master/demo/demo2.gif)