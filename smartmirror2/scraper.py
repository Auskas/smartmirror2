#! python3
# scraper.py - the module is used to scrape web sites.

import aiohttp
import asyncio
import async_timeout
import logging
import time
import bs4
import threading

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
        self.url_calendar = 'https://www.sports.ru/spartak/calendar/'
        self.url_news = 'https://www.newsru.com'
        self.url_covid = 'https://www.worldometers.info/coronavirus/'
        self.logger.debug('An instance of Scraper has been created.')
        self.news_string = ''
        self.rates_string = ''
        self.covid_figures = [
            '24,925,950', '861,668', '18,209,780',
            '1,000,500', '+4,952',
            '17,414', '+31',
            '821,169'
        ]
        rates_loop = self.loop.create_task(self.ratesbot())
        news_loop = self.loop.create_task(self.newsbot())
        covid_loop = self.loop.create_task(self.covidbot())            

    async def get_page(self, link):
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(link) as resp:
                    if resp.status != 200:
                        self.logger.error(f'Cannot get {link}.\n Status {resp.status}')
                        return False
                    else:
                        return await resp.text()
        except Exception as error:
            self.logger.error(f'Cannot load the page, the following error occured: {error}')
            return False

    def rates_parser(self, res):
        """ Uses 'yandex.ru' to obtain stocks data."""
        values = []
        changes = []
        if res == False:
            return None
        try:
            self.logger.debug(f'Page {self.url_yandex} has been loaded!')
            soup = bs4.BeautifulSoup(res, features='html.parser')        
            rates = soup.find_all('span', class_='inline-stocks__value_inner')
            if len(rates) < 3:
                self.logger.error('Cannot find the rates on the page.')
                self.rates_string = ''
            for rate in rates:
                values.append(rate.getText())
            directions = soup.find_all('span', class_='a11y-hidden')
            if len(directions) < 3:
                self.logger.error('Cannot find the rates delta on the page.')
                changes = ['','','']
            else:
                for direction in directions:
                    if direction.getText()[0] == '+':
                        changes.append('↑')
                    elif direction.getText()[0] == '-':
                        changes.append('↓')
                    else:
                        changes.append('')
            self.rates_string = f'$ {values[0]}{changes[0]}   € {values[1]}{changes[1]}   Brent {values[2]}{changes[2]}'
            self.logger.info('Got the string for the latest exchange rates.')
        except Exception as exc:
            self.logger.error(f'Cannot update the exchange rates: {exc}')

    def news_parser(self, res):
        """ Downloads the webpage http://newsru.com. 
        Finds the main news on the page.
        Also finds other news on the page."""
        new_news = []
        self.logger.debug(f'Page {self.url_news} has been loaded!')
        if res == False:
            return None
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
                self.news_string = ''.join(new_news)
                #print(self.news_string)
            self.logger.info('Got the latest news.')
        except Exception as exc:
            self.logger.error(f'Cannot update the news: {exc}')

    def covid_parser(self, res):
        self.logger.debug(f'Page {self.url_covid} has been loaded!')
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
        self.covid_figures = temp_figures
        self.logger.info('Got the Covid-19 latest figures.')
        #self.logger.debug(' '.join(self.covid_figures))
        #self.logger.info(f'Processing time {time.perf_counter() - st_time}')

    async def ratesbot(self):
        while True:
            res = await self.get_page(self.url_yandex)
            if res == False:
                await asyncio.sleep(60)
            else:
                rates_parser_thread = threading.Thread(target=self.rates_parser, args=(res,))
                rates_parser_thread.start()
                await asyncio.sleep(3600)

    async def newsbot(self):
        while True:
            res = await self.get_page(self.url_news)
            if res == False:
                await asyncio.sleep(60)
            else:
                news_parser_thread = threading.Thread(target=self.news_parser, args=(res,))
                news_parser_thread.start()
                await asyncio.sleep(3600)

    async def covidbot(self):
        while True:
            res = await self.get_page(self.url_covid)
            if res == False:
                await asyncio.sleep(3600)
            else:
                covid_parser_thread = threading.Thread(target=self.covid_parser, args=(res,))
                covid_parser_thread.start()
                await asyncio.sleep(43200)

    async def main(self):
        #rates_loop = self.loop.create_task(self.ratesbot())
        news_loop = self.loop.create_task(self.newsbot())
        covid_loop = self.loop.create_task(self.covidbot())
        test_loop = self.loop.create_task(self.test())


if __name__ == '__main__':   
    loop = asyncio.get_event_loop()
    scraper = Scraper(loop)
    scraper.main()
    loop.run_forever()

__version__ = '0.01' # 20.11.2019    
