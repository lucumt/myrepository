'''
Spider Module
'''
# -*- coding: utf-8 -*-

from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request

from datetime import date

import urlparse
import re

from release.items import ReleaseItem


class ReleaseSpider(Spider):

    name = 'release-spider'
    allowed_domains = ['eia.gov']

    def start_requests(self):
        for year in range(2008, date.today().year+1):
            yield Request("http://www.eia.gov/pressroom/releases.cfm?year="+bytes(year), callback=self.parse_style_one)
        for year in range(1997, 2008):
            yield Request("http://www.eia.gov/pressroom/archive/press/months"+bytes(year)+".htm", callback=self.parse_style_two)

    def parse_style_one(self, response):
        sel = Selector(response)
        records = sel.xpath('//div[@class="pagecontent mr_temp1"]/div[@class="main_col"]/div[@class="items press"]/span')
        for record in records:
            ritem = ReleaseItem()
            ritem['source'] = 'EIA'
            ritem['type'] = 'Press Release'
            ritem['where'] = 'Fed'
            date = record.xpath('p[@class="tagline"]/text()').extract()
            if date:
                ritem['date'] = date[0]
            ritem['title'] = record.xpath('h5/a/text()').extract()[0]
            url = record.xpath('h5/a/@href').extract()[0]
            url = urlparse.urljoin(response.url, url)
            ritem['url'] = url
            yield Request(url, meta={'item':ritem}, callback=self.parse_summary)

    def parse_style_two(self,response):
        sel = Selector(response)
        links = sel.xpath('//div[@class="main_col"]//a[@href]')
        hrefs = set()
        records = []
        for link in links:
            href = link.xpath('@href').extract()[0]
            if href not in hrefs:
                hrefs.add(href)
                records.append(link)
        for record in records:
            ritem = ReleaseItem()
            ritem['source'] = 'EIA'
            ritem['type'] = 'Press Releases'
            ritem['where'] = 'Fed'
            title = record.xpath('text()').extract()
            if not title:
                title = record.xpath('font/text()').extract()
            if title:
                title = title[0].replace('\r', '').replace('\n', '')
                title = re.sub(r'\s+', ' ', title)
                ritem['title'] = title
            url = record.xpath('@href').extract()[0]
            url = urlparse.urljoin(response.url, url)
            ritem['url'] = url
            date = record.xpath('following-sibling::em/text()').extract()
            if date:
                date = date[0].replace('\r', '').replace('\n', '').strip()
                ritem['date'] = date
            yield Request(url, meta={'item':ritem}, callback=self.parse_summary)

    def parse_summary(self,response):
        sel = Selector(response)
        ritem = response.meta['item']
        summary = sel.xpath('//div[@class="main_col"]//h1/following-sibling::p[1]')
        if not summary:
            summary = sel.xpath('//p[@class="CategoryTitle"]/following-sibling::p[1]')
        if not summary:
            summary = sel.xpath('//td[contains(.,"WHAT")]/following-sibling::td[1]')
            paragraphs = summary.xpath('p')
            if paragraphs:
                summary = summary.xpath('p[1]')
        if not summary:
            summary = sel.xpath('//h3[@class="CategoryTitle"]/following-sibling::p[1][@class="report_summary"]')
        if not summary:
            summary = sel.xpath('//h3[@class="CategoryTitle"]/following-sibling::div[1][@class="report_summary"]')
        if not summary:
            summary = sel.xpath('//div[@align="center"]/p[@class="CategoryTitle"]/..')
            if summary:
                summary = summary.xpath('following-sibling::p[1][@class="report_summary"]')
        if not summary:
            summary = sel.xpath('//div[@align="center"][@class="CategoryTitle"]/following-sibling::p[@class="report_summary"][1]')
        if not summary:
            summary = sel.xpath('//p[@align="center"][@class="CategoryTitle"]/strong/..')
            if summary:
                summary = summary.xpath('following-sibling::p[1]')
        if not summary:
            summary = sel.xpath('//p[@class="report_summary"]/span[@class="CategoryTitle"]/..')
            if summary:
                summary = summary.xpath('following-sibling::p[@class="report_summary"][1]')
        if not summary:
            summary = sel.xpath('//center/p/span[@class="CategoryTitle"]/../..')
            if summary:
                summary = summary.xpath('following-sibling::p[@class="report_summary"][1]')
        if not summary:
            summary = sel.xpath('//center/h3[@class="CategoryTitle"]/..')
            if summary:
                summary = summary.xpath('following-sibling::p[1]')
        if not summary:
            summary = sel.xpath('//div[@align="center"]/span[@class="CategoryTitle"]/..')
            if summary:
                summary = summary.xpath('following-sibling::p[@class="report_summary"][1]')
        if not summary:
            summary = sel.xpath('//h4[@align="center"][@class="CategoryTitle"]/following-sibling::span[@class="report_summary"][1]')
        if not summary:
            summary = sel.xpath('//p[@class="MsoTitle"]/following-sibling::p[1]')
        if not summary:
            summary = sel.xpath('//h3/center/span[@class="CategoryTitle"]/../..')
            if summary:
                summary = summary.xpath('following-sibling::p[@class="report_summary"][1]')
        if not summary:
            summary = sel.xpath('//div[@align="center"][@class="report_summary"]/following-sibling::p[@class="report_summary"][1]')
        if not summary:
            summary = sel.xpath('//p[@class="CategoryTitle"]/b/..')
            if summary:
                summary = summary.xpath('following-sibling::span[@class="report_summary"][1]')
        if not summary:
            summary = sel.xpath('//center/span[@class="CategoryTitle"]/b/../..')
            if summary:
                summary = summary.xpath('following-sibling::p[@class="report_summary"][1]')
        if not summary:
            summary = sel.xpath('//center/span[@class="CategoryTitle"]/font/b/../../..')
            if summary:
                summary = summary.xpath('following-sibling::p[@class="report_summary"][1]')
        if not summary:
            summary = sel.xpath('//p[@align="center"][@class="report_summary"]')

        if summary:
            summarycontents = summary.xpath('descendant-or-self::text()').extract()
            if summarycontents is not None and isinstance(summarycontents, list):
                ritem['summary'] = ''.join(summarycontents)
            else:
                ritem['summary'] = summarycontents[0]
            ritem['summary'] = ritem['summary'].replace('\r', '').replace('\n', '')
            
        return ritem