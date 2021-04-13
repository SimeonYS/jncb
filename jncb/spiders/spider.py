import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import JjncbItem
from itemloaders.processors import TakeFirst

pattern = r'(\xa0)?'
base = 'https://www.jncb.com/About-Us/News-Room/News?page={}'

class JjncbSpider(scrapy.Spider):
	name = 'jncb'
	page = 1
	start_urls = [base.format(page)]

	def parse(self, response):
		post_links = response.xpath('//article/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		if len(post_links) == 15:
			self.page += 1
			yield response.follow(base.format(self.page), self.parse)


	def parse_post(self, response):
		date = response.xpath('//section[@class="general-content wrap-news-content"]/h3/following-sibling::text()').get()
		date = re.findall(r'\d+\s\w+\s\d+', date)
		title = response.xpath('//section[@class="general-content wrap-news-content"]/h3/text()').get()
		content = response.xpath('//section[@class="general-content wrap-news-content"]//text()[not (ancestor::h3 or ancestor::h2 or ancestor::div[@id="atstbx"])]').getall()[3:]
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=JjncbItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
