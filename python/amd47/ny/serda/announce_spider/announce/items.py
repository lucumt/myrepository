"""
Announce spider item module
"""
# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class AnnounceItem(Item):

    date = Field()
    title = Field()
    url = Field()
    summary = Field()
    source = Field()
    type = Field()
