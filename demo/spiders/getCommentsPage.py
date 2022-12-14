import scrapy
import json

from .. items import CommentItem
from scrapy.utils.response import open_in_browser
from scrapy.exceptions import CloseSpider

class CommentsPageSpider(scrapy.Spider):
    name = "cmt"
    plain_fb = "https://mbasic.facebook.com"

    page = "/blvanhquan"
    def start_requests(self):
            yield scrapy.Request(self.plain_fb + self.page + '?v=timeline', callback=self.authorize)

    def authorize(self, response):
        yield scrapy.FormRequest.from_response(
                response,
                formxpath='//form[contains(@action, "login")]',
                formdata={'email': '0587756618','pass': 'Phanvu151001'},
                callback=self.parseTimeLine,
                meta = {'year': 2022}
                )

    def parseTimeLine(self, response):
        for post in response.xpath("//article[contains(@data-ft,'top_level_post_id')]")[1:2]:     
            href = post.xpath(".//a[contains(@href,'footer')]/@href").extract_first()
            yield scrapy.Request(self.plain_fb + href, callback=self.parsePost)
        """ open_in_browser(response) """
        
        more_path = "//a[contains(@href,'stream/?cursor')]/@href"
        new_page = response.xpath(more_path).extract_first()

        if new_page:
            new_page = self.plain_fb + new_page

            try:
                yield scrapy.Request(new_page, 
                            callback=self.parseTimeLine, meta={'year': response.meta['year']})
            except:
                yield scrapy.Request(new_page, 
                                            callback=self.parseTimeLine)
        else:
            year = response.meta['year'] - 1
            year_path = "//span[contains(text(),'%s')]/parent::*/@href" % year

            new_page = response.xpath(year_path).extract_first()
            if new_page:
                new_page = self.plain_fb + new_page
                yield scrapy.Request(new_page, 
                                            callback=self.parseTimeLine, 
                                            meta={'year':year})
            else:
                CloseSpider('Finished!!!')


    def parseUtil(self, cmt):
        src = cmt.xpath('.//h3/a/text()').extract_first().strip()
        content = cmt.xpath('.//div[h3]/div[1]//text()').extract()
        print(content)

        if len(content) == 0:
            content = 'text not found'

        item = CommentItem()
        item['src'] = src
        item['content'] = content

        return item

    def parseReplyPage(self, response):
        #parse replies comment
        
        replies_path = '//div[contains(@id,"root")]/div/div/div[count(@id)=1 and contains("0123456789", substring(@id,1,1))]'
        replies_cmt = response.xpath(replies_path)

        for cmt in replies_cmt:
            item = self.parseUtil(cmt)
            item['post_url'] = response.meta['post_url']
            item['reply_to'] = response.url
            yield item

        #view more replies
        more_path = '//span[contains(text(),"previous rep")]/parent::a/@href'
        new_page = response.xpath(more_path).extract_first()
        if new_page:
            new_page = self.plain_fb + new_page
            yield scrapy.Request(new_page,
                                    callback=self.parseReplyPage)
        


    def parsePost(self, response):
        non_reply_path = './/div[string-length(@class) = 2 and count(@id)=1 and contains("0123456789", substring(@id,1,1)) and not(.//div[contains(@id,"comment_replies")])]'
        for cmt in response.xpath(non_reply_path):
            item = self.parseUtil(cmt)
            item['post_url'] = response.url
            yield item


        reply_path = '//div[string-length(@class) = 2 and count(@id)=1 and contains("0123456789", substring(@id,1,1)) and .//div[contains(@id,"comment_replies")]]'
        for cmt in response.xpath(reply_path):
            item = self.parseUtil(cmt)
            item['post_url'] = response.url
            yield item

            reply_page = cmt.xpath('.//a[contains(@href,"repl")]/@href').extract_first()
            yield scrapy.Request(self.plain_fb + reply_page, callback=self.parseReplyPage, meta={'post_url': response.url})

        #view more
        more_path = './/div[contains(@id,"see_next")]/a/@href'
        new_page = response.xpath(more_path).extract_first()

        if new_page:
            new_page = self.plain_fb + new_page
            yield scrapy.Request(new_page,
                                    callback=self.parsePost)     

        
