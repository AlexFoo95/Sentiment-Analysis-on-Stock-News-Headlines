import psycopg2

from nltk.corpus import stopwords
import re
from nltk.tokenize import word_tokenize
from nltk import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()

conn = psycopg2.connect(host="localhost", database="StockMarket", user="postgres", password="dihi04cuqe")
cur = conn.cursor()

lexicon = []
filter_line = []
filter_lexicon = []
filter_word = []
word_index = []
special_chars = re.compile("[^A-Za-z0-9 ]+")
hm_lines = 100000
stop_words = set(stopwords.words('english'))

postgreSQL_select_Query = """ select * from public."dataset" """
cur.execute(postgreSQL_select_Query)
dataset_records = cur.fetchall()

for line in dataset_records:
    data = line[1]
    data = data.lower().replace("<br />", " ")
    data = re.sub(special_chars,"", data.lower())
    filter_line.append(data)

for l in filter_line[:hm_lines]:
    all_words = word_tokenize(l)
    all_words = [lemmatizer.lemmatize(i) for i in all_words]
    lexicon += list(all_words)

for word in lexicon:
    if word not in filter_word:
        filter_word.append(word)

for word in filter_word:
    if word not in stop_words:
        sql = """INSERT INTO public."token"("token_vocab") VALUES ('%s');""" %(word)
        cur.execute(sql)

conn.commit()
cur.close()




