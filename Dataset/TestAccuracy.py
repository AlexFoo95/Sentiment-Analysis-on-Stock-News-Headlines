import psycopg2
import xlsxwriter
import time
import os
from Predict import predict
from SentimentDataset import load_predict_info
from sklearn.metrics import accuracy_score
from sklearn.metrics import precision_recall_fscore_support as score

#--- retrieve all the labels from each news headlines from db
def TestAccurate():
    conn = psycopg2.connect(host="localhost", database="StockMarket", user="postgres", password="dihi04cuqe")
    cur = conn.cursor()
    postgreSQL_select_Query = """ select * from public."testdataset" """
    cur.execute(postgreSQL_select_Query)
    dataset_records = cur.fetchall()
    train = []
    for row in dataset_records:
        result = row[2]
        train.append(result)

    return train

#--- retrieve only the news headlines from test dataset and predict
def PredictTestData():
    token_vocab, label_vocab = load_predict_info()
    times = str(time.strftime("%d%m%Y%H%M%S"))
    filename = "PredictOutput_testing_" + times + ".xlsx"
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    worksheet.write(0, 0, 'News Headlines')
    worksheet.write(0, 1, 'Polarity')
    worksheet.write(0, 2, 'Probability')

    rows = 1
    col = 0
    conn = psycopg2.connect(host="localhost", database="StockMarket", user="postgres", password="dihi04cuqe")
    cur = conn.cursor()
    postgreSQL_select_Query = """ select * from public."testdataset" """
    cur.execute(postgreSQL_select_Query)
    news = cur.fetchall()
    Predict= []
    for row in news:
        article = row[1]
        print(article)
        polarity, probability = predict(token_vocab, label_vocab, article)
        Predict.append(polarity)
        worksheet.write(rows, col, article)
        worksheet.write(rows, col + 1, polarity)
        worksheet.write(rows, col + 2, probability)
        rows += 1

    workbook.close()
    os.startfile(filename)
    return Predict

if __name__ == '__main__':
    y_true = TestAccurate()
    y_pred = PredictTestData()
    #--- cal the testing accuracy by compare the annotated results with the predicted result
    result = accuracy_score(y_true,y_pred)
    result = str(result)
    print(" The accuracy for the model is " + result + '\n')

    precision, recall, fscore, support = score(y_true, y_pred)
    print('labels:    [Positive Neutral Negative]')
    print('precision: {}'.format(precision))
    print('recall:    {}'.format(recall))
    print('fscore:    {}'.format(fscore))
    print('support:   {}'.format(support))