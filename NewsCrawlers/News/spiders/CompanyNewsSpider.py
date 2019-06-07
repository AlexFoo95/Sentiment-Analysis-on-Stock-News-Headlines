import psycopg2
import requests
from bs4 import BeautifulSoup
from scrapy import Spider
from scrapy.http.request import Request
from w3lib.url import add_or_replace_parameter
from Predict import predict
from SentimentDataset import load_predict_info
from News.items import NewsItem
import re
from dateutil import parser

class ComSpider(Spider):
    name = 'Comspider'

    #-----retrieve the stock code of all the company
    conn = psycopg2.connect(host="localhost", database="StockMarket", user="postgres", password="dihi04cuqe")
    cur = conn.cursor()
    postgreSQL_select_Query = """ select * from public."company" """
    cur.execute(postgreSQL_select_Query)
    company = cur.fetchall()
    Comdata = []
    count = 0
    for row in company:
        company_id = row[2]
        Comdata.append(company_id)
        count = count + 1

    #----- first url that will crawl
    start_urls = [
        "https://www.malaysiastock.biz/Corporate-Infomation.aspx?securityCode=0001"
    ]

    #----- url that use during the iteration
    single_url = 'https://www.malaysiastock.biz/Corporate-Infomation.aspx?='

    #----- the main process
    def parse(self, response):

        #--- get the total number of the company
        max_page = ComSpider.count

        #--- for loop that crawl multiple pages that based different stock code
        for page in range(0, max_page + 1):
            #--- get the stock code
            code = ComSpider.Comdata[page]

            #--- call the scrape function iterally
            yield Request(
                url = add_or_replace_parameter(self.single_url,'securityCode',code),
                callback=self.scrape,
                meta = {'code': code})

    def scrape(self, response):
        single_url = 'https://www.malaysiastock.biz/Corporate-Infomation.aspx?securityCode='
        #--- retrieve the tokens and labels
        token_vocab, label_vocab = load_predict_info()
        article = NewsItem()
        i = 0
        alldata = []
        imgsrc = 0
        StockCode = response.meta.get('code')

        completeurl = single_url + StockCode
        conn = psycopg2.connect(host="localhost", database="StockMarket", user="postgres", password="dihi04cuqe")
        cur = conn.cursor()

        #x = HtmlXPathSelector(response)
        r = requests.get(completeurl)
        #--- crawl the news
        all_links = response.css('.tablelist td span a')
        # iterate over links
        print(completeurl, '\n')
        for sel in all_links:
            try:
                html_as_string = r.text
                soup = BeautifulSoup(html_as_string, 'html.parser')
                article['headline'] = (soup.select(".line td span a"))[i].text
                article['link'] = response.css('.tablelist td span a').xpath('@href').extract()[i]
                article['code'] = StockCode
                # --- filter the news headlines that are not in english language
                if re.findall('[\u4e00-\u9fff]+', article['headline']):
                    if "News" in article['link']:
                        imgsrc = imgsrc + 1

                # --- filter the news headlines to prevent duplication problem
                else:
                    postgreSQL_select_Query = """ select * from public."company_news" """
                    cur.execute(postgreSQL_select_Query)
                    news = cur.fetchall()
                    Newsexist = False
                    for row in news:
                        if article['headline'] == row[1] and article['code'] == row[5]:
                            Newsexist = True
                            if "News" in article['link']:
                                imgsrc = imgsrc + 1

                    # --- if the news headline does not exist in the db, then predict and store
                    if Newsexist == False:
                        singledata = []

                        if "Blog" in article['link']:
                            print(article['link'])
                            b = requests.get(article['link'])
                            html_as_string = b.text
                            p = BeautifulSoup(html_as_string, 'html.parser')
                            # article['source'] = response.css('.line td a').xpath('text()').extract()
                            article['source'] = p.find('label', {'id': 'MainContent2_lbAuthorProfile'}).find('a').text
                            data = p.find('label', {'id': 'MainContent2_lbAuthorProfile'}).text
                            unusedata, date = data.split('e:')
                            date = date.strip()
                            date = str(date)
                            for item in date.splitlines():
                                d = parser.parse(item)
                                article['time'] = d.strftime("%Y-%m-%d")

                            polarity, probability = predict(token_vocab, label_vocab, article['headline'])
                            probability = str(probability)
                            singledata.append(article['headline'])
                            singledata.append(article['link'])
                            singledata.append(polarity)
                            singledata.append(probability)
                            singledata.append(article['code'])
                            singledata.append(article['source'])
                            singledata.append(article['time'])
                            alldata.append(singledata)
                            print(i, article['headline'])
                            print('link:', article['link'])
                            print('published time:', article['time'])
                            print('polarity:', polarity)
                            print('source:', article['source'])

                        else:
                            print(article['link'])
                            article['source'] = response.css('.line td a img').xpath('@src').extract()[imgsrc]
                            if 'thestar' in article['source']:
                                s = requests.get(article['link'])
                                html_as_string = s.text
                                s = BeautifulSoup(html_as_string, 'html.parser')
                                date = s.find('p', {'class': 'date'})

                                if date == None:
                                    article['time'] = None

                                else:
                                    date = s.find('p', {'class': 'date'}).text
                                    date = date.replace(' ', '')
                                    date = date.strip()
                                    date = str(date)

                                    for item in date.splitlines():
                                        d = parser.parse(item)
                                        article['time'] = d.strftime("%Y-%m-%d")

                            else:
                                s = requests.get(article['link'])
                                html_as_string = s.text
                                s = BeautifulSoup(html_as_string, 'html.parser')
                                date = s.find('span', {'class': 'post-created'})
                                if date is None:
                                    article['time'] = None

                                else:
                                    date = s.find('span', {'class': 'post-created'}).text
                                    date = str(date.lower())

                                    if date is '':
                                        article['time'] = None

                                    else:
                                        if 'am' in date:
                                            date = date.replace('am', '')

                                        if 'pm' in date:
                                            date = date.replace('pm', '')

                                        for item in date.splitlines():
                                            d = parser.parse(item)
                                            article['time'] = d.strftime("%Y-%m-%d")

                            polarity, probability = predict(token_vocab, label_vocab, article['headline'])
                            probability = str(probability)
                            singledata.append(article['headline'])
                            singledata.append(article['link'])
                            singledata.append(polarity)
                            singledata.append(probability)
                            singledata.append(article['code'])
                            singledata.append(article['source'])
                            singledata.append(article['time'])
                            alldata.append(singledata)
                            print(i, article['headline'])
                            print('link:', article['link'])
                            print('published time:', article['time'])
                            print('polarity:', polarity)
                            print('source:', article['source'])
                            imgsrc = imgsrc + 1

                i = i + 1
            except:
                print("The news headline had some error or does not exist.")


        for news_num in range(len(alldata), 0, -1):
            news_num = news_num - 1
            if alldata[news_num][6] is None:
                print("The news is not exit or got errors.")

            else:
                sql = """INSERT INTO public."company_news"("news_title", "news_link", "news_time", "news_accuracy", "news_code", "news_source", "news_polarity" ) VALUES ( %s, %s, %s, %s, %s, %s, %s);"""
                data = (alldata[news_num][0], alldata[news_num][1], alldata[news_num][6], alldata[news_num][3], alldata[news_num][4], alldata[news_num][5], alldata[news_num][2])
                cur.execute(sql, data)
                conn.commit()


        cur.close()

        #yield article
