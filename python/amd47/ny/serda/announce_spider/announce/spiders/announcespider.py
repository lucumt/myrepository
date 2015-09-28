'''Announce spider module'''
# -*- coding: utf-8 -*-

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request

from datetime import date as dt

from announce.items import AnnounceItem

import urlparse

class AnnounceSpider(Spider):
    '''Announce spider class'''

    name = 'announce-spider'
    allowed_domains = ['nyserda.ny.gov']

    def start_requests(self):
        baseurl = 'http://www.nyserda.ny.gov/About/Newsroom/'
        for year in range(2012, dt.today().year+1):
            yield Request(baseurl+bytes(year)+'-Announcements.aspx', callback=self.parse_item)

    def parse_item(self, response):

        sel = Selector(response)
        items = []
        records = sel.xpath('//ul[@class="extrapaddedList"]/li')
        for record in records:
            aitem = AnnounceItem()
            aitem['date'] = record.xpath('span[@class="announce-date"]/text()').extract()[0].strip()
            aitem['title'] = record.xpath('a/text()').extract()[0].strip()
            url = record.xpath('a/@href').extract()[0].strip()
            url = urlparse.urljoin(response.url, url)
            aitem['url'] = url
            aitem['summary'] = record.xpath('span[@class="announce-subhead"]/text()').extract()[0].strip()
            aitem['source'] = ' NYSERDA'
            aitem['type'] = 'Announcements'
            items.append(aitem)
        return items
