#coding:utf-8

import scrapy
import logging
import re
import os
import bs4
from bs4 import BeautifulSoup
import urllib.parse


logger = logging.getLogger('baike spider')

class BaikeSpider(scrapy.Spider):
    name = 'baike'
    website_possible_httpstatus_list = [301, 302]
    baike_url = 'http://baike.baidu.com/'
    view_url = 'http://baike.baidu.com/view/'
    DIR_HTML = 'data/baike_html/'
    dir_no = 0
    dir_number = 0
    url_to_crawl_number = 1
    last_url_number = 0
    url_group_number = 10000
    url_expand_number = 3
    url_end_number = 20000000

    def start_requests(self):
        urls = [
        ]
        
        while True:
            if os.path.exists(self.DIR_HTML+str(self.dir_no)):
                self.dir_no += 1
                self.last_url_number += self.url_group_number
            else:
                if os.path.exists(self.DIR_HTML+str(self.dir_no-1)):
                    self.dir_number = len(os.listdir(self.DIR_HTML+str(self.dir_no-1)))
                    if self.dir_number < self.url_group_number:
                        self.dir_no -= 1
                        self.last_url_number = self.last_url_number - self.url_group_number + self.dir_number
                    else:
                        os.mkdir(self.DIR_HTML+str(self.dir_no))
                        self.dir_number = 0
                else:
                    self.dir_number = 0
                    self.dir_no = 0
                    os.mkdir(self.DIR_HTML+str(self.dir_no))
                break

        if os.path.exists('last_url_number'):
            with open('last_url_number', 'r') as f:
                self.last_url_number = max(int(f.read()), self.last_url_number)

        while self.url_to_crawl_number < min(self.last_url_number + self.url_group_number, self.url_end_number):
            urls.append(self.view_url + str(self.url_to_crawl_number) + '.htm')
            self.url_to_crawl_number += 1
        for url in urls:
            yield scrapy.Request(url)

    def parse(self, response):
        if response.body == 'banned':
            request = response.request
            request.meta['change_proxy'] = True
            yield request
        else:
            if self.last_url_number % self.url_group_number == 0:
                with open('last_url_number', 'w') as f:
                    f.write(str(self.last_url_number))
            self.last_url_number += 1
            if response.url.find('error') != -1:
                pass
            else:
                logging.info('got page: %s' % response.url)
                soup = BeautifulSoup(response.body, 'lxml')
                baike_name = str(soup.title.text)
                baike_name.replace('/', '_')
                if self.dir_number == self.url_group_number:
                    self.dir_no += 1
                    self.dir_number = 0
                    os.mkdir(self.DIR_HTML+str(self.dir_no))
                self.dir_number += 1
                with open(os.path.join(self.DIR_HTML+str(self.dir_no), baike_name) + '.html', 'wb') as f:
                    f.write(response.body)
            if self.url_to_crawl_number - self.last_url_number < self.url_group_number:
                n = min(self.url_to_crawl_number + self.url_expand_number * self.url_group_number, self.url_end_number)
                while self.url_to_crawl_number < n:
                    next_url = self.view_url + str(self.url_to_crawl_number) + '.htm'
                    self.url_to_crawl_number += 1
                    yield scrapy.Request(next_url)

    @classmethod
    def is_item(cls, href):
        return href and re.compile('item').search(href)

    @classmethod
    def get_format_text(cls, tag):
        text = str(tag.text)
        img_tags = tag.find_all('a', attrs={'class': 'lemma-album'})
        for img_tag in img_tags:
            text = text.replace(str(img_tag.text) + '\n', '')
        description_tags = tag.find_all(attrs={'class': 'description'})
        for description_tag in description_tags:
            text = text.replace(str(description_tag.text) + '\n', '')
        text = re.sub(r'\[\d+\]\xa0', '', text)
        text = text.replace('\n\n', '\n')
        text = re.sub(r'^\n', '', text)
        text = re.sub(r'\n$', '', text)
        return text
