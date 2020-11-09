#!/usr/bin/python3
# scraper.py - the module is used to scrape web sites.
# The module combines both asynchronous and multiprocessing approaches.
# aiohttp is used to obtain data from web sites.
# multiprocessing is used to process the obtained data.
# Current parsers: news, exchange rates, covid rates, weather.

import os
import aiohttp
import asyncio
import logging
import time
import bs4
from multiprocessing import Process, Queue
import requests

class Scraper:
    
    def __init__(self, asyncloop):
        self.logger = logging.getLogger('SM.scraper')
        self.loop = asyncloop
        if __name__ == '__main__': # Creates a logger if the module is called directly.
            ch = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            ch.setFormatter(formatter)
            self.logger.setLevel(logging.DEBUG)
            self.logger.addHandler(ch)
        self.url_yandex = 'https://yandex.ru/'
        self.url_news = 'https://www.newsru.com'
        self.url_covid = 'https://www.worldometers.info/coronavirus/'
        self.url_weather = 'https://api.weather.yandex.ru/v1/informers?'
        self.logger.debug('An instance of Scraper has been created.')
        self.news_string = '   *** Загрузка новостей ***   '
        self.rates_string = '*** Обновление данных по котировкам ***'
        self.covid_figures = [
            '24,925,950', '861,668', '18,209,780',
            '1,000,500', '+4,952',
            '17,414', '+31',
            '821,169'
        ]
        self.forecast_string = None

        self.yandex_weather_token = os.environ.get('YANDEX_WEATHER_TOKEN')
        if self.yandex_weather_token == None:
            self.logger.debug('Cannot get YANDEX_WEATHER_TOKEN environment variable')
        else:
            self.logger.debug('YANDEX_WEATHER_TOKEN environment variable found')

        queue = Queue()
        rates_loop = self.loop.create_task(self.ratesbot(queue))
        news_loop = self.loop.create_task(self.newsbot(queue))
        covid_loop = self.loop.create_task(self.covidbot(queue)) 
        if self.yandex_weather_token is not None:
            weather_loop = self.loop.create_task(self.weatherbot(queue))
        receiver_loop = self.loop.create_task(self.process_receiver(queue))

    async def get_page(self, link: str, response_type='text', payload='', headers=''):
        """ Loads the provided link in the asynchronous way.
            Returns the page data on success, otherwise, returns False."""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(link, params=payload, headers=headers) as resp:
                    if resp.status != 200:
                        self.logger.error(f'Cannot get {link}\n Status {resp.status}')
                        return False
                    else:
                        self.logger.debug(f'{link} loaded')
                        if response_type == 'text':
                            return await resp.text()
                        elif response_type == 'json':
                            return await resp.json()
        except Exception as error:
            self.logger.error(f'Cannot load the page, the following error occured: {error}')
            return False

    def rates_parser(self, res: str, queue):
        """ Arguments: res - page data in the string format;
                       queue - multiprocessing Queue instanse.
                Processes the data to find the exchange rates and their deltas.
                Forms a string that represents the exchange rates of USD to RUB,
            EUR to RUB, oil price, and their deltas. On failure returns None.
                On success puts a dictionary with the key 'rates_string' and 
            the string as the value into the queue."""
        values = []
        deltas = []
        try:
            soup = bs4.BeautifulSoup(res, features='html.parser')        
            rates = soup.find_all('span', class_='inline-stocks__value_inner')
            if len(rates) < 3:
                self.logger.warning('Cannot find the rates on the page.')
                return None
            for rate in rates:
                values.append(rate.getText())
            directions = soup.find_all('span', class_='a11y-hidden')
            if len(directions) < 3:
                self.logger.warning('Cannot find the rates delta on the page.')
                return None
            else:
                for direction in directions:
                    if direction.getText()[0] == '+':
                        deltas.append('↑')
                    elif direction.getText()[0] == '-':
                        deltas.append('↓')
                    else:
                        deltas.append('')
            queue.put({'rates_string': f'$ {values[0]}{deltas[0]}   € {values[1]}{deltas[1]}   Brent {values[2]}{deltas[2]}'})
            self.logger.info('Got the string for the latest exchange rates.')
        except Exception as exc:
            self.logger.error(f'Cannot update the exchange rates: {exc}')

    def news_parser(self, res: str, queue):
        """ Arguments: res - page data in the string format;
                       queue - multiprocessing Queue instanse.
                Processes the data to find the main news on the page.
                Forms a string that represents the news separated by the three
            asterisks. 
                On success puts a dictionary with the key 'news_string' and 
            the string as the value into the queue."""
        new_news = []
        try:
            soup = bs4.BeautifulSoup(res, features='html.parser')
            mainNewsTitle = soup.find('div', class_='sp-main-title')
            mainNewsText = soup.find('div', class_='sp-main-text')
            new_news.append('. '.join([mainNewsTitle.getText().strip(), mainNewsText.getText().strip()]) + '   ***   ')
            newsTags = soup.find_all('div', class_='left-feed-text')
            number_of_news = 1
            for tag in newsTags:
                tagTitle = tag.find('div', class_ = 'left-feed-title')
                tagText = tag.find('div', class_= 'left-feed-anons')
                new_news.append(tagTitle.getText().strip() + '   ***   ')
                number_of_news += 1
                if number_of_news == 10:
                    break
            if len(new_news) > 0:
                queue.put({'news_string': ''.join(new_news)})
                self.logger.info('Got the latest news.')
            else:
                self.logger.warning('Cannot find the news on the page')
        except Exception as exc:
            self.logger.error(f'Cannot update the news: {exc}')

    def covid_parser(self, res: str, queue):
        """ Arguments: res - page data in the string format;
                       queue - multiprocessing Queue instanse.
                Processes the data to find the number of COVID-19 cases.
                Forms a list that represents the number of cases, deaths,
            and recoveries in the world, and in Russia, as well as
            the number of recent cases and deaths.
                On success puts a dictionary with the key 'covid_figures' and 
            the list as the value into the queue."""
        try:
            st_time = time.perf_counter()
            temp_figures = []
            soup = bs4.BeautifulSoup(res, features='html.parser')
            figures = soup.find_all('div', class_='maincounter-number')
            for figure in figures:
                temp_figures.append(figure.getText().replace('\n',''))
            national_figures = soup.find_all('tr')
            for nation in national_figures:
                country = nation.getText()
                if country.find('Russia') != -1:
                    temp_figures.extend(country.split()[2:7])
                    break
            if len(temp_figures) > 7:
                queue.put({'covid_figures': temp_figures})
                self.logger.info('Got the Covid-19 latest figures.')
            else:
                self.logger.warning('Cannot find the Covid-19 figures on the page')
        except Exception as exc:
            self.logger.error(f'Cannot update the Covid-19 figures: {exc}')

    async def ratesbot(self, queue):
        """ Argument: queue - multiprocessing Queue instanse.
                The method is async. It periodically loads 'https://yandex.ru/'
                and passes the results to a separate process that parses the data."""
        while True:
            res = await self.get_page(self.url_yandex)
            if res == False:
                await asyncio.sleep(600)
            else:
                rates_parser_process = Process(target=self.rates_parser, args=(res, queue))
                rates_parser_process.start()
                await asyncio.sleep(3600)

    async def newsbot(self, queue):
        """ Argument: queue - multiprocessing Queue instanse.
                The method is async. It periodically loads 'https://www.newsru.com'
                and passes the results to a separate process that parses the data."""
        while True:
            res = await self.get_page(self.url_news)
            if res == False:
                await asyncio.sleep(60)
            else:
                news_parser_process = Process(target=self.news_parser, args=(res, queue))
                news_parser_process.start()
                
                await asyncio.sleep(3600)

    async def covidbot(self, queue):
        """ Argument: queue - multiprocessing Queue instanse.
                The method is async. It periodically loads 
                'https://www.worldometers.info/coronavirus/'
                and passes the results to a separate process that parses the data."""
        while True:
            res = await self.get_page(self.url_covid)
            if res == False:
                await asyncio.sleep(60)
            else:
                covid_parser_process = Process(target=self.covid_parser, args=(res, queue))
                covid_parser_process.start()
                await asyncio.sleep(43200)

    async def weatherbot(self, queue):
        """ Argument: queue - multiprocessing Queue instanse.
                The method is async. It periodically gets 
                'https://api.weather.yandex.ru/v1/informers?'"""
        lat = '55.716848' # latitude of the forecast (Moscow)
        lon = '37.882962' # longitude of the forecast (Moscow)
        lang = 'ru_RU'    # language of the reply (Russian)
        payload = {'lat': lat, 'lon': lon, 'lang': lang}
        headers = {'X-Yandex-API-Key': self.yandex_weather_token}
        while True:
            res = await self.get_page(self.url_weather, 'json', payload, headers)
            if res == False:
                await asyncio.sleep(60)
            else:
                self.forecast_string = res
                await asyncio.sleep(43200)

    async def process_receiver(self, queue):
        """ Argument: queue - multiprocessing Queue instanse.
                The method is asynchronously waits for dictionaries in the queue.
                If there are expected keys it assigns the values to the
                dedicated variables."""
        while True:
            if queue.empty():
                await asyncio.sleep(1)
            else:
                data = queue.get()
                try:
                    for key in data.keys():
                        if key == 'news_string':
                            self.news_string = data[key]
                        elif key == 'rates_string':
                            self.rates_string = data[key]
                        elif key == 'covid_figures':
                            self.covid_figures = data[key]
                        else:
                            self.logger.warning(f'Got unknown key from a proceess: {key}')
                except Exception as exc:
                    self.logger.warning(f'Cannot process the data in the queue {exc}')

if __name__ == '__main__':   
    loop = asyncio.get_event_loop()
    scraper = Scraper(loop)
    loop.run_forever()

__version__ = '0.96' # 10th September 2020
__author__ = 'Dmitry Kudryashov'
__maintainer__ = 'Dmitry Kudryashov'
__email__ = "dmitry-kud@yandex.ru"    
__status__ = "Development"
