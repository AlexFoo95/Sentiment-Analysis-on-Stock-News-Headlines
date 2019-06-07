from scrapy.crawler import CrawlerProcess
from crawler.News.spiders.LatestNewsSpider import LatestSpider
from crawler.News.spiders.CompanyNewsSpider import ComSpider

if __name__ == '__main__':
    #run both crawlers
    process = CrawlerProcess()
    process.crawl(LatestSpider)
    process.crawl(ComSpider)
    process.start()
