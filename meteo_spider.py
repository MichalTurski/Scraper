import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta

class QuotesSpider(scrapy.Spider):
    name = "meteo"
    start_urls = [
        'https://meteomodel.pl/dane/historyczne-dane-pomiarowe/',
    ]

    def __init__(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(15)

    def __parse_header(self, row):
        headers = []
        for column in row.xpath('td'):
            title = column.xpath('@title').get(),
            text = column.xpath('text()').get(),
            if not title[0]:
                headers.append(text)
            else:
                headers.append(title)
#            for h in headers:
#                yield {
#                    "b": h
#                }
        return headers

    def __parse_row(self, row, headers, date):
        j = 0
        meas = dict()
        meas["Data"] = date.strftime("%d-%m-%Y")
        for column in row.xpath('td'):
            text = column.xpath('text()').get()
            a = column.xpath('a//text()').get()
            if not text:
                meas[headers[j][0]] = a
            else:
                meas[headers[j][0]] = text
            j += 1
        return meas

    def parse(self, response):
        self.driver.get(response.url)
        
        date = datetime(2019, 2, 28)
        count = 0
        while True:
            #prev = self.driver.find_element_by_xpath('//input[@id="btnPrev"]')
            rows = response.xpath('//table[@id="tablepl"]//tr')
            i = 0
            for row in rows[1:]:
                if i == 0:  # get names from second line
                    headers = self.__parse_header(row)
                else:
                    dane = self.__parse_row(row, headers, date)
                    yield dane
                i += 1
            date = date - timedelta(days=1)
            count += 1         
            try:
                prev = self.driver.find_element_by_xpath('//input[@id="btnPrev"]')
                #prev = WebDriverWait(self.driver, 30).until(
                #    EC.element_to_be_clickable((By.ID, '//input[@id="btnPrev"]'))
                #)
                prev.click() 
                #if count >= 5:
                #    raise Exception('Loop end')
            except:
                break
        self.driver.close()

