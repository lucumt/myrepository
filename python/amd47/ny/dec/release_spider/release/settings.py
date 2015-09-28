'''Spider settings module'''
# -*- coding: utf-8 -*-

# Scrapy settings for nyDecPressReleases project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'release'

SPIDER_MODULES = ['release.spiders']
NEWSPIDER_MODULE = 'release'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'release.spider (+http://www.yourdomain.com)'
