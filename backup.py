"""         reply_path = './/div[string-length(@class) = 2 and count(@id)=1 and contains("0123456789", substring(@id,1,1)) and .//div[contains(@id,"comment_replies")]]'
        for cmt in response.xpath(reply_path):
            answer = cmt.xpath('.//a[contains(@href,"repl")]/@href').extract()
            ans = response.urljoin(answer[::-1][0])
            yield scrapy.Request(ans,
                                 callback=self.parseReply, meta={'post_url': response.url})

    def parseReply(self, response):

        root_path = '//div[contains(@id,"root")]/div/div/div[count(@id)!=1 and contains("0123456789", substring(@id,1,1))]'

        for cmt in response.xpath(root_path):
            item = CommentItem()
            item['src'] = cmt.xpath(".//h3/a/text()").extract_first().strip()
            item['content'] = cmt.xpath(".//div//text()").extract_first().strip()
            item['post_url'] = response.meta['post_url']
        
        replies = []
        for reply in response.xpath('//div[contains(@id,"root")]/div/div/div[count(@id)=1 and contains("0123456789", substring(@id,1,1))]'): 
            print(reply.xpath(".//div[h3]/div[1]//text()").extract_first().strip())

        item['replies'] = replies
        yield item """