'''Regional spider module'''
# -*- coding: utf-8 -*-

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request

import urlparse

from regional.items import RegionalItem


class RegionalSpider(Spider):

    '''Regional spider'''

    name = 'regional-spider'
    allowed_domains = ['dec.ny.gov']
    start_urls = ['http://www.dec.ny.gov/press/77537.html']

    regions = {}

    def parse(self, response):
        sel = Selector(response)
        regionrecords = sel.xpath('//div[@id="contentContainer"]/p[3]/strong/a')
        for region in regionrecords:
            regionkey = region.xpath('text()').extract()[0]
            regionvalue = region.xpath('../following-sibling::strong/text()').extract()[0] + region.xpath('../following-sibling::strong/following-sibling::text()').extract()[0].strip()
            self.regions[regionkey] = regionvalue
        region = sel.xpath('//div[@id="contentContainer"]/p[3]/a/strong')[0]
        regionkey = region.xpath('text()').extract()[0]
        regionvalue = region.xpath('../following-sibling::strong/text()').extract()[0]+region.xpath('../following-sibling::strong/following-sibling::text()').extract()[0]
        self.regions[regionkey] = regionvalue
        records = sel.xpath('//ul[@class="toc"]/li')
        for record in records:
            ritem = RegionalItem()
            ritem['source'] = 'NY DEC'
            ritem['type'] = 'Regional Press Releases'
            ritem['title'] = record.xpath('a/text()').extract()[0]
            recordcontent = record.xpath('text()').extract()[0]
            ritem['date'] = recordcontent[3:11]
            region = recordcontent[14:]
            ritem['summary'] = region
            if self.regions.has_key(region):
                ritem['summary'] += ' ' + self.regions[region]
            url = record.xpath('a/@href').extract()[0]
            url = urlparse.urljoin(response.url, url)
            ritem['url'] = url
            yield Request(url, meta={'item':ritem}, callback=self.parse_item)

    def parse_item(self, response):
        '''
        Parse the first paragraph content
        '''
        sel = Selector(response)
        ritem = response.meta['item']
        firstparagraph = sel.xpath('//div[@id="contentContainer"]/p[3]/text()').extract()[0]
        ritem['summary'] = ritem['summary'] + ' ' + firstparagraph
        return ritem
