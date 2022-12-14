# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class CommentItem(scrapy.Item):
    # define the fields for your item here like:
    src = scrapy.Field()
    content = scrapy.Field()
    reply_to = scrapy.Field()
    post_url = scrapy.Field()
    
