import re
import scrapy
from scrapy.http import HtmlResponse
import hashlib

class ReviewsSpider(scrapy.Spider):
    name = "cars"

    start_urls = [
        'https://www.cars.com/dealers/208308/haus-auto-group/reviews/',
    ]

    data = {}
    reviews = []
    pagination = []
    lower_limit = 0
    upper_limit = 0
        
    def __init__(self):
        self.called = False
        
    def parse(self, response):

        global data, reviews, pagination, lower_limit,upper_limit
        
        if not self.called:
            self.called = True
            
            self.data["website"] = response.css('title::text').get()
            self.data["biz_logo_link"] = response.css('img.dealer__logo::attr(src)').get()
            self.data["post_site_url"] = response.request.url
            base_url = re.search('https?://([A-Za-z_0-9.-]+).*', response.request.url)
            self.data["post_review_link"] = response.request.url
            self.data["biz_favicon"] =  response.css('link[rel="icon"]::attr(href)').get()

            try:
                for next_page in response.css('div.page-section__container ul.pagination-links li a::attr(href)').getall():
                    if next_page is not None:
                        num = re.findall(r'[0-9]+', next_page)[-1]
                        if num not in self.pagination:
                            self.pagination.append(num)
                self.lower_limit = int(self.pagination[0])
                self.upper_limit = int(self.pagination[-1])
            except:
                pass
  
        for tag in response.css('div.dealer-dpp-section__review-cards ul li').getall():
            tag_response = HtmlResponse(url="HTML string", body=tag, encoding='utf-8')
            try:
                date_ = tag_response.css('div.dealer-review__card-body div.dealer-card__date::text').get() 
            except:
                date_ = ''
            try:
                name_ = tag_response.css('div.dealer-review__card-body div.dealer-card__byline span.dealer-card__username::text').get() 
            except:
                name_ = ''
            try:
                title_ = tag_response.css('div.dealer-review__card-body div.dealer-card__subject a::text').get()
            except:
                title_ = ''
            try:
                rating_ = tag_response.css('div.star-rating span::text').get()
            except:
                rating_ = ''
            try:
                source_ = tag_response.css('div.dealer-review__card-body div.dealer-card__byline span.dealer-card__user_location::text').get()
            except:
                source_ = ''
            try:
                desc = []
                for span in tag_response.css('div.cui-section__accordion div.dealer-card__body p span::text').getall():
                    desc.append(span)
                desrciption_ = ". ".join(desc)
            except:
                desciption_ = ''
            
            data_items = {}

            data_items['name'] = name_
            data_items['date'] = date_
            data_items['avatar'] = ""
            data_items['rating'] = rating_
            data_items['title'] = title_
            data_items['description'] = desrciption_
            data_items['source'] = source_

            strId = f'{name_}{date_}'
            #Assumes the default UTF-8
            hash_object = hashlib.md5(strId.encode())
            data_items['reviewId'] = hash_object.hexdigest()

            self.reviews.append(data_items)
  
        if self.lower_limit <= self.upper_limit:
            try:
                page = "?start=" + str(self.lower_limit)
                self.lower_limit  += 1
                yield response.follow(page, callback=self.parse)
            except:
                pass
        else:              
            self.data["reviews"] = self.reviews
            yield self.data
            
###script author:https://github.com/mujahidalkausari?###
