import scrapy
from functools import partial

class NewsSpider(scrapy.Spider):
    name = "news"

    def start_requests(self):
        url = 'https://luatvietnam.vn/Ajax/GetViewByCateId_Paging?languageid=0&usingDisplayTable=0&paginationType=0' \
              '&fieldId=0&effectStatusId=0&organId=0&docTypeId=0&updateTargetId=ArticlesByCateBox&insertionMode' \
              '=Replace&controllerName=Ajax&actionName=GetViewByCateId_Paging&pageSize=25&linkLimit=3&docid=0' \
              '&docGroupId=0&registTypeId=0&relatetypeid=0&provinceid=0&year=0&LawTerminGroupId=0&messageTypeId=0' \
              '&isMyMessage=False&categoryId=186&tagId=0&searchOptions=0&signerId=0&transactionStatusId=0' \
              '&isSearchExact=0&showNumberOfResults=100&page=1&X-Requested-With=XMLHttpRequest '
        yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        item_list = response.css(".item-list ")
        for item in item_list:
            thumbnail = item.css(".item-list ")[0].css("img::attr(src)").extract_first()
            published_date = item.css(".item-list ")[0].css(".post-time-page::text")[-1].extract().strip()
            headline = item.css(".item-list ")[0].css(".post-thumbnail a::attr(title)").extract()
            link = item.css(".item-list ")[0].css(".post-thumbnail a::attr(href)").extract_first()
            if len(item.css(".sapo span::text")) != 0:
                continue
            list_text = item.css(".sapo div::text").extract()
            if len(list_text) == 0:
                list_text = item.css(".sapo p::text").extract()
            for text in list_text:
                text.replace('\xa0', ' ')
            list_link_text = item.css(".sapo a::text").extract()
            for index, text in enumerate(list_link_text):
                list_text.insert(index * 2 + 1, text)
            if not list_text[0][0].isupper():
                list_text = list_text[::-1]
            brief = ' '.join(list_text)
            news_dict =  {
                'link_to_news': link,
                'headlines': headline,
                'published_date': published_date,
                'image': thumbnail,
                'brief': brief
            }
            yield response.follow(url='https://luatvietnam.vn'+link,
                                  callback=partial(self.get_news_html, news_dict=news_dict),
                                  dont_filter=True)

    def get_news_html(self,response,news_dict):
        news_dict['news_html'] = response.css(".post-inner").extract_first()
        yield news_dict