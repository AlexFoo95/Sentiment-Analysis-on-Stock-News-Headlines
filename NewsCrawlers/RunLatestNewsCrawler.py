
from scrapy.crawler import CrawlerProcess
from crawler.News.spiders.LatestNewsSpider import LatestSpider
from crawler.News.spiders.CompanyNewsSpider import ComSpider

if __name__ == '__main__':
    #run only latest news crawler
    process = CrawlerProcess()
    process.crawl(LatestSpider)
    process.start()

