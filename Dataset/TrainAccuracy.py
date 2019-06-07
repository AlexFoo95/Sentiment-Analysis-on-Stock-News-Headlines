import psycopg2
from Predict import predict
from SentimentDataset import load_predict_info
from sklearn.metrics import accuracy_score

#--- retrieve all the labels from each news headlines from db
def TrainAccurate():
    conn = psycopg2.connect(host="localhost", database="StockMarket", user="postgres", password="dihi04cuqe")
    cur = conn.cursor()
    postgreSQL_select_Query = """ select * from public."traindataset" """
    cur.execute(postgreSQL_select_Query)
    dataset_records = cur.fetchall()
    train = []
    for row in dataset_records:
        text = row[2]
        train.append(text)

    return train

#--- retrieve only the news headlines from train dataset and predict
def PredictTrainData():
    token_vocab, label_vocab = load_predict_info()
    conn = psycopg2.connect(host="localhost", database="StockMarket", user="postgres", password="dihi04cuqe")
    cur = conn.cursor()
    postgreSQL_select_Query = """ select * from public."traindataset" """
    cur.execute(postgreSQL_select_Query)
    news = cur.fetchall()
    Predict= []
    for row in news:
        article = row[1]
        polarity, probability = predict(token_vocab, label_vocab, article)
        Predict.append(polarity)

    return Predict

if __name__ == '__main__':
    y_true = TrainAccurate()
    y_pred = PredictTrainData()
    # --- cal the training accuracy by compare the annotated results with the predicted result
    result = accuracy_score(y_true,y_pred)
    result = str(result)
    print(" The accuracy for the training data is " + result)