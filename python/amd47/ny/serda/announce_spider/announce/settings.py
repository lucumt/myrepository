# -*- coding: utf-8 -*-

# Scrapy settings for announce_spider project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'announce_spider'

SPIDER_MODULES = ['announce.spiders']
NEWSPIDER_MODULE = 'announce.spiders'

#DOWNLOAD_DELAY=100

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'announce_spider (+http://www.yourdomain.com)'
