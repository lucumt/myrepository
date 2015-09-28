'''Spider moudle'''
# -*- coding: utf-8 -*-

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request
import urlparse

from release.items import ReleaseItem

class ReleaseSpider(Spider):
    '''Release Spider'''
    name = 'release-spider'
    allowed_domains = ['dec.ny.gov']
    start_urls = ['http://www.dec.ny.gov/press/press.html', 'http://www.dec.ny.gov/press/100188.html', 'http://www.dec.ny.gov/press/95079.html', 'http://www.dec.ny.gov/press/88018.html']

    def parse(self, response):
        sel = Selector(response)
        records = sel.xpath('//ul[@class="toc"]/li')
        for record in records:
            ritem = ReleaseItem()
            ritem['title'] = record.xpath('a/text()').extract()[0]
            ritem['type'] = 'Press Releases'
            ritem['source'] = 'NY DEC'
            ritem['date'] = record.xpath('text()').extract()[0][3:]
            url = record.xpath('a/@href').extract()[0]
            url = urlparse.urljoin(response.url, url)
            ritem['url'] = url
            yield Request(url, meta={'item':ritem}, callback=self.parse_item)

    def parse_item(self, response):
        '''Parse the summary information'''
        sel = Selector(response)
        ritem = response.meta['item']
        ritem['summary'] = sel.xpath('//p[@class="releaseInfo"]/following-sibling::h1/following-sibling::p/text()').extract()[0]
        return ritem
