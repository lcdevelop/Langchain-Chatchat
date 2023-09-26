from typing import Iterable
import scrapy
from scrapy import Selector, Request
import json
from scrapy.http import Request
from scrapy.http.response.html import HtmlResponse


class EastmoneySpider(scrapy.Spider):
    name = "eastmoney"
    allowed_domains = ["data.eastmoney.com", "pdf.dfcfw.com"]

    def start_requests(self):
        for page in range(100):
            yield Request(url=f'https://reportapi.eastmoney.com/report/list?cb=datatable2309463&industryCode=447&pageSize=100&industry=*&rating=*&ratingChange=*&beginTime=2021-09-25&endTime=2023-09-25&pageNo={page}&fields=&qType=1&orgCode=&rcode=&p=2&pageNumber=2&_=1695604884459')

    def parse(self, response: HtmlResponse):
        print(response.url)
        ret_text = response.text
        ret_text = ret_text[ret_text.index('(')+1:-1]
        ret_json = json.loads(ret_text)

        data = ret_json['data']
        for item in data:
            url = 'https://data.eastmoney.com/report/zw_industry.jshtml?infocode=' + \
                item['infoCode']
            yield Request(url=url, callback=self.parseDetail)

    def parseDetail(self, response: HtmlResponse):
        pdf_url = response.selector.css(
            'body > div.main > div.main > div.zw-content > div.left > div.ctx-box > div.ctx-body > div.c-foot > span.to-pre > a::attr(href)').extract_first()
        print('pdf:', pdf_url)
        yield Request(url=pdf_url, callback=self.parsePdf)

    def parsePdf(self, response: HtmlResponse):
        path = 'result/' + response.url.split('/')[-1]
        with open(path, "wb") as f:
            f.write(response.body)
        print('save pdf ok', path)
