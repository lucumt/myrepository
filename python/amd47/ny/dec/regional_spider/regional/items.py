'''Item module'''
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class RegionalItem(Item):

    '''Item to store the crawled data'''

    title = Field()
    url = Field()
    date = Field()
    summary = Field()
    type = Field()
    source = Field()
