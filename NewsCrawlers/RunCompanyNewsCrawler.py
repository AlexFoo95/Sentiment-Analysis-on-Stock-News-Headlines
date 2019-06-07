from scrapy.crawler import CrawlerProcess
from crawler.News.spiders.CompanyNewsSpider import ComSpider

if __name__ == '__main__':
    #run only company crawler
    process = CrawlerProcess()
    process.crawl(ComSpider)
    process.start()

