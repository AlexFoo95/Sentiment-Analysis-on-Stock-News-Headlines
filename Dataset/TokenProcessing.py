import psycopg2
from normalise import normalise
from nltk.corpus import stopwords
import re
from nltk.tokenize import word_tokenize
from nltk import WordNetLemmatizer
lemmatizer = WordNetLemmatizer()



def ProcessToken():
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

        #--- retrieve all data from the train dataset table
        postgreSQL_select_Query = """ select * from public."traindataset" """
        cur.execute(postgreSQL_select_Query)
        dataset_records = cur.fetchall()

        #--- from the data, get all the news headlines
        for line in dataset_records:
            data = line[1]
            #--- replace all empty tag with spacebar
            data = data.replace("<br />", " ")
            #--- replace all special chars with spacebar
            data = re.sub(special_chars," ", data)
            # append the headlines into array
            filter_line.append(data)

        for l in filter_line[:hm_lines]:
            #--- tokenise the headlines
            all_words = word_tokenize(l)
            #--- normalise all the token
            all_words = normalise(all_words, verbose=True)
            #--- change all token into lower case
            all_words = [w.lower() for w in all_words]
            #--- lemmatize the token
            all_words = [lemmatizer.lemmatize(i) for i in all_words]
            #--- save all the token into another array
            lexicon += list(all_words)

        #--- remove the duplicated token
        for word in lexicon:
            if word not in filter_word:
               filter_word.append(word)

        #--- if the token is not a stop words, then save the token into db
        for word in filter_word:
            sql = """INSERT INTO public."token2"("token_vocab") VALUES ('%s');""" %(word)
            cur.execute(sql)

            print("The token: " + word +" had been stored in the database.")

        conn.commit()
        cur.close()

if __name__ == '__main__':
    ProcessToken()


