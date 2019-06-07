import psycopg2
from scrapy import Spider
from Predict import predict
from SentimentDataset import load_predict_info
from News.items import NewsItem
import requests
from bs4 import BeautifulSoup
import re
from dateutil import parser


class LatestSpider(Spider):
    name = 'Bizspider'
    start_urls = [
        "https://www.malaysiastock.biz/Blog/Blog-Headlines.aspx",
    ]

    # --- the main process
    def parse(self, response):
        token_vocab,label_vocab = load_predict_info()
        article= NewsItem()
        i = 0
        imgsrc = 0
        blogsrc = 0
        alldata = []
        all_links = response.css('td .newsHeadline a')
        conn = psycopg2.connect(host="localhost", database="StockMarket", user="postgres", password="dihi04cuqe")
        cur = conn.cursor()

        r = requests.get('https://www.malaysiastock.biz/Blog/Blog-Headlines.aspx')
        # --- crawl the latest news
        for sel in all_links:
            try:
                html_as_string = r.text
                soup = BeautifulSoup(html_as_string, 'html.parser')
                article['headline'] = soup.findAll('span', {'class': 'newsHeadline'})[i].text
                article['link'] = response.css('td .newsHeadline a').xpath('@href').extract()[i]
                # --- filter the news headlines that are not in english language
                if re.findall('[\u4e00-\u9fff]+', article['headline']):
                    #print("The news headline is not in english language")
                    if "Blog" in article['link']:
                        blogsrc = blogsrc + 1

                    else:
                        imgsrc = imgsrc + 1

                # --- filter the news headlines to prevent duplication problem
                else:
                    postgreSQL_select_Query = """ select * from public."latest_news" """
                    cur.execute(postgreSQL_select_Query)
                    news = cur.fetchall()
                    Newsexist = False
                    for row in news:
                        if article['headline'] == row[1] and article['link'] == row[2]:
                            #print("The news headline had existed in the database.")
                            Newsexist = True
                            if "Blog" in article['link']:
                                blogsrc = blogsrc + 1

                            else:
                                imgsrc = imgsrc + 1

                    # --- if the news headline does not exist in the db, then predict and store
                    if Newsexist == False:
                        singledata = []
                        if "Blog" in article['link']:
                            print(article['link'])
                            article['source'] = response.css('td .newsMedia a').xpath('text()').extract()[blogsrc]
                            b = requests.get(article['link'])
                            html_as_string = b.text
                            p = BeautifulSoup(html_as_string, 'html.parser')
                            data = p.find('label', {'id': 'MainContent2_lbAuthorProfile'}).text
                            unusedata, date = data.split('e:')
                            date = date.strip()
                            date = str(date)
                            for item in date.splitlines():
                                d = parser.parse(item)
                                article['time'] = d.strftime("%Y-%m-%d %H:%M")
                            polarity, probability = predict(token_vocab, label_vocab, article['headline'])
                            probability = str(probability)
                            singledata.append(article['headline'])
                            singledata.append(article['link'])
                            singledata.append(polarity)
                            singledata.append(probability)
                            singledata.append(article['source'])
                            singledata.append(article['time'])
                            alldata.append(singledata)
                            print('\n')
                            print(i, article['headline'])
                            print('link:', article['link'])
                            print('published time:', article['time'])
                            print('polarity:', polarity)
                            print('source:', article['source'])
                            print('\n')
                            blogsrc = blogsrc + 1

                        else:
                            print(article['link'])
                            article['source'] = response.css('td span a img').xpath('@src').extract()[imgsrc]
                            if 'thestar' in article['source']:
                                s = requests.get(article['link'])
                                html_as_string = s.text
                                s = BeautifulSoup(html_as_string, 'html.parser')
                                date = s.find('p', {'class': 'date'})

                                if date == None:
                                    article['time'] = None

                                else:
                                    date = s.find('p', {'class': 'date'}).text
                                    time = s.find('time', {'class': 'timestamp'}).text
                                    date = date.replace(' ', '')
                                    date = date.strip()
                                    date = str(date)
                                    time = time.replace(' ', '')
                                    time = time.strip()
                                    time = str(time)
                                    datetime = date + " " + time
                                    if time is '':
                                        othertime = response.css('.line td').xpath('text()').extract()[i]
                                        datetime = date + " " + othertime
                                    print(datetime)

                                    if 'MYT' in datetime:
                                        datetime = datetime.replace('MYT', '')

                                    for item in datetime.splitlines():
                                        d = parser.parse(item)
                                        article['time'] = d.strftime("%Y-%m-%d %H:%M")


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
                                            article['time'] = d.strftime("%Y-%m-%d %H:%M")

                            polarity, probability = predict(token_vocab, label_vocab, article['headline'])
                            probability = str(probability)
                            singledata.append(article['headline'])
                            singledata.append(article['link'])
                            singledata.append(polarity)
                            singledata.append(probability)
                            singledata.append(article['source'])
                            singledata.append(article['time'])
                            alldata.append(singledata)
                            print('\n')
                            print(i, article['headline'])
                            print('link:', article['link'])
                            print('published time:', article['time'])
                            print('polarity:', polarity)
                            print('source:', article['source'])
                            print('\n')
                            imgsrc = imgsrc + 1


                i = i + 1
            except:
                print("The news headline had some error or does not exist.")


        for news_num in range(len(alldata), 0, -1):
            news_num = news_num - 1
            if alldata[news_num][5] is None:
                print("The news is not exit or got errors.")

            else:
                sql = """INSERT INTO public."latest_news"("news_title", "news_link", "news_polarity", "news_accuracy", "news_source", "news_time") VALUES ( %s, %s, %s, %s, %s, %s);"""
                data = (alldata[news_num][0], alldata[news_num][1], alldata[news_num][2], alldata[news_num][3],alldata[news_num][4], alldata[news_num][5])
                cur.execute(sql, data)
                conn.commit()

        cur.close()