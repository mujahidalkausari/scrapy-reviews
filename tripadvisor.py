import re
import scrapy
from scrapy.http import HtmlResponse
import hashlib

class ReviewsSpider(scrapy.Spider):
    name = "tripadvisor"

    start_urls = [
        'https://www.tripadvisor.ca/Hotel_Review-g60982-d87016-Reviews-Hilton_Hawaiian_Village_Waikiki_Beach_Resort-Honolulu_Oahu_Hawaii.html',
    ]

    data = {}
    reviews = []
    pagination = []
        
    def __init__(self):
        self.called = False
        
    def parse(self, response):

        global data, reviews, pagination
        
        if not self.called:
            self.called = True
            
            self.data["website"] = response.css('title::text').get()
            self.data["biz_logo_link"] = response.css('img[alt="Tripadvisor"]::attr(src)').get()
            post_site_url = response.request.url
            self.data["post_site_url"] = post_site_url
            base_url = re.search('https?://([A-Za-z_0-9.-]+).*', post_site_url)
            reviews_link = response.css('div._2cefqRQ2 a::attr(href)').get()
            self.data["post_review_link"] = f'https://{base_url.group(1)}{reviews_link}'
            self.data["biz_favicon"] =  response.css('link[rel="icon"]::attr(href)').get()

        
            next_pages = response.css('div[data-test-target="reviews-tab"] div._16gKMTFp div.pageNumbers a::attr(href)').getall()

            if next_pages is not None:
                for nextpage in next_pages:
                    page_url = f'https://{base_url.group(1)}{nextpage}'
                    self.pagination.append(page_url)    
            
        for tag in response.css('div[data-test-target="reviews-tab"] div[data-test-target="HR_CC_CARD"]').getall():
            tag_response = HtmlResponse(url="HTML string", body=tag, encoding='utf-8')
            try:
                date_ = tag_response.css('div._2fxQ4TOx span::text').get().split("review")[1]  
            except:
                date_ = ''
            try:
                name_ = tag_response.css('div._2fxQ4TOx span a::text').get()
            except:
                name_ = ''
            try:
                title_ = tag_response.css('div[data-test-target="review-title"] a span span::text').get() 
            except:
                title_ = ''
            try:
                rating_ = int(tag_response.css('div[data-test-target="review-rating"] span::attr(class)').get().split("_")[3])/10
            except:
                rating_ = ''
            try:
                avatar_ = int(str(tag_response.css('div._310S4sqz a.ui_social_avatar img::attr(src)').get()))
            except:
                avatar_ = ''
            try:
                desc_text = []
                desc_text.append(str(tag_response.css('div._3hDPbqWO q span::text').get()))

                try:
                    desc_text.append(str(tag_response.css('div._3hDPbqWO q span._1M-1YYJt::text').get()))
                except:
                    pass
                review = ' .'.join(desc_text)
                desciption_ = re.sub(u"(\u2018|\u2019)", "'", review)
            except:
                desciption_ = ''
            
            data_items = {}

            data_items['name'] = name_
            data_items['date'] = date_
            data_items['avatar'] = avatar_
            data_items['rating'] = rating_
            data_items['title'] = title_
            data_items['description'] = desciption_
            data_items['source'] = ""
            
            strId = f'{name_}{date_}'
            #Assumes the default UTF-8
            hash_object = hashlib.md5(strId.encode())
            data_items['reviewId'] = hash_object.hexdigest()

            self.reviews.append(data_items)
            
        if len(self.pagination) > 0:
            page = self.pagination[0]
            self.pagination.pop(0)
            yield response.follow(page, callback=self.parse)
        else:
                    
            self.data["reviews"] = self.reviews
            yield self.data
            
###script author:https://github.com/mujahidalkausari?###
