# Sentiment-Analysis-on-Stock-News-Headlines

1. The News Crawlers will crawls the news headlines from the stock news website.
2. The RNN models will carry out the sentiment analysis on the stock news that had been crawled.
3. Database that had been used was the PostgreSQL. The stock news information, together with the 
   sentiment analysis results will be store in the database.
4. SATestingGUI is just a simple interface which allow the user to insert some news headlines 
   and predict the polarity.
   
# Important Setting
- Pycharm IDE had been used.
- Please change the database setting in the codes.
- Change the RNN directories.

# Program Setup
### RNN setup
1.	Create database table – token, traindataset, testdataset, labels
2.	Remove the Trained_models folder and the Final_graph.tf.pb file if the items are present in the RNN folder.
3.	Run:
    -	SaveTestingDataset.py in Dataset folder
    -	SaveTrainingDataset.py in Dataset folder
    -	SaveLabel.py in Dataset folder
4.	Run:
    -	TokenProcessing.py to get all the tokens, the tokens will be saved in database.
5.	Run:
    -	TrainRNN.py in RNN folder to train the RNN model.
    -	TestAccuracy.py in Dataset folder to test the accuracy of the model.
6.	If the user wants to skip the RNN setup, then skip step 5, since the RNN had already built and train.

### Stock Company
1.	Create database table – company 
2.	Run:
    -	SaveCompany.py to save all the stock company in the database.
    -	The data in the company table will be used by the crawler to crawl the company stock news.

### Web Crawlers
1.	Create database table – latest_news, company_news
2.	Insert the news from the LatestCrawledNews folder into the database tables
3.	Run:
    -	RunBothNewsCrawler.py to crawl the latest stock news and the company stock news.
    -	RunCompanyNewsCrawler.py to crawl only the company stock news.
    -	RunLatestNewsCrawler.py to crawl only the company stock news.
4.	The sentiment analysis of the news headlines will be carried out once receive stock news by the crawlers.

### Sentiment Analysis Testing Desktop Application
1.	Run:
    -	SystemTestingGUI.py to start the application.
