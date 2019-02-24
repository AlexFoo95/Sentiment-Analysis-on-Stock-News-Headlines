import codecs,re
import copy
import psycopg2
import random
from nltk.tokenize import word_tokenize
from nltk import WordNetLemmatizer
from nltk.corpus import stopwords
lemmatizer = WordNetLemmatizer()




class Vocab:
    def __init__(self, mode='token'):
        self.mode = mode
        self.token_unk_id = 0  # in 'token.vocab.txt', the id of '_UNK' is 0.
        self.token_unk_symbol = '_UNK'  # 'UNK' means unknown word, a word that doesn't exist the vocabulary set.

        self.token_pad_id = 1  # in 'token.vocab.txt', the id of '_PAD' is 1.
        self.token_pad_symbol = '_PAD'  # 'PAD' means non-character on 128 blank.

        self.token_2_id = {}  # input from Vocab.load_token_vocab() / output to Vocab.get_id()
        self.id_2_token = {}  # input from Vocab.load_token_vocab() / output to Vocab.get_symbol()

        self.labels_2_id = {}  # input from Vocab.load_target_vocab() / output to Vocab.get_id()
        self.id_2_labels = {}  # input from Vocab.load_target_vocab() / output to Vocab.get_symbol()

        self.target_out_symbol = 'O'

        if mode == 'token': self.load_token()
        if mode == 'label': self.load_labels()

    def load_token(self):
        conn = psycopg2.connect(host="localhost", database="StockMarket", user="postgres", password="dihi04cuqe")
        cur = conn.cursor()
        postgreSQL_select_Query = """ select * from public."token" """
        cur.execute(postgreSQL_select_Query)
        token_records = cur.fetchall()
        for row in token_records:
            id = row[0]
            token = row[1]
            id = int(id)

            if token == self.token_unk_symbol:
                self.token_2_id[token] = self.token_unk_id
                continue

            if token == self.token_pad_symbol:
                self.token_2_id[token] = self.token_pad_id
                continue

                    # other tokens
            self.token_2_id[token] = id
            self.id_2_token[id] = token


        cur.close()
        conn.close()


    def load_labels(self):
        conn = psycopg2.connect(host="localhost", database="StockMarket", user="postgres", password="dihi04cuqe")
        cur = conn.cursor()
        postgreSQL_select_Query = """ select * from public."labels" """
        cur.execute(postgreSQL_select_Query)
        labels_records = cur.fetchall()
        for row in labels_records:
            id = row[0]
            id = int(id)
            label = row[1]

            self.labels_2_id[label] = id
            self.id_2_labels[id] = label


    def get_id(self, symbol):
        if self.mode == 'token':
            return self.token_2_id.get(symbol, self.token_unk_id)

        if self.mode == 'label':
            return self.labels_2_id.get(symbol)


    def get_symbol(self, id):
        if self.mode == 'token':
            return self.id_2_token.get(id)

        if self.mode == 'label':
            return self.id_2_labels.get(id)

    def get_num_tokens(self):
        if self.mode == 'token': return len(self.token_2_id)
        return None

    def get_num_targets(self):
        if self.mode == 'label': return len(self.labels_2_id)
        return None

    def get_token_pad_id(self):
        return self.token_pad_id

    def get_target_null_id(self):
        return self.get_id(self.target_out_symbol)


class DatasetItem:
    def __init__(self, label, text):
        self.label = label
        self.text = text

        self.label_id = None
        self.token_ids = None  # it should be array

    def set_id(self, label_id, token_ids):
        self.label_id = label_id
        self.token_ids = token_ids

    def get_tokens(self):
        # currently, only support 'character'
        return list(self.text)



class TextProcessing:
    def __init__(self, src=None, mode='file'):  # mode = 'file' | 'sentence'
        self.data = []

        if mode == 'file':      self.load_text_file_data()
        if mode == 'sentence':  self.load_text_data(src)

    def add_to_data(self, target, text):
        # normalize
        target = target.upper()
        #text = text.upper()
        self.data.append(DatasetItem(target, text))

    def load_text_data(self, line):
        # mode = 'sentence'
        # format of line : "TAG  \t  SENTENCE"
        line = line.rstrip('\n\r')
        target, text = line.split('\t')
        text = text.strip()
        self.add_to_data(target, text)

    def load_text_file_data(self):
        # mode = 'file'
        special_chars = re.compile("[^A-Za-z0-9 ]+")
        stop_words = set(stopwords.words('english'))
        conn = psycopg2.connect(host="localhost", database="StockMarket", user="postgres", password="dihi04cuqe")
        cur = conn.cursor()
        postgreSQL_select_Query = """ select * from public."dataset" """
        cur.execute(postgreSQL_select_Query)
        dataset_records = cur.fetchall()
        for row in dataset_records:
            filter_text = []
            text = row[1]
            text = text.lower().replace("<br />", " ")
            text = re.sub(special_chars, "", text.lower())
            text = word_tokenize(text)
            text = [lemmatizer.lemmatize(i) for i in text]
            for words in text:
                if words not in stop_words:
                    filter_text.append(words)

            target = row[2]
            self.add_to_data(target, filter_text)

        cur.close()
        conn.close()


class Epoch():
    def __init__(self, id_data, batch_size, num_steps, target_num_step=None, pad_id=1, label_null_id=0,
                 deterministic=False):
        self.data = id_data  # it should be id-based data

        self.token_pad_id = pad_id
        self.label_null_id = label_null_id

        self.batch_size = batch_size
        self.num_steps = num_steps

        self.src_num_steps = num_steps
        self.tar_num_steps = target_num_step  # for sequence to sequence dataset

        self.deterministic = deterministic  # if deterministic is True, data is shuffled and retrieved
        self.iterator = self.iterate_forever()  # during trian, shuffle index
        self.predict_iterator = self.iterate_once()  # during test, don't shuffle index

        self.epoch = 0

    def get_num_examples(self):
        return len(self.data)

    def get_batch_size(self):
        return self.batch_size

    def get_epoch_num(self):
        return self.epoch

    def _iterate(self, index_gen, batch_size, max_len):
        """ Abstraction method for _iterate function"""
        raise NotImplementedError("Abstract method.".format(self.run.__name__))

    # for training
    def iterate_forever(self):
        def index_stream():
            # yield data index
            self.indexs = list(range(self.get_num_examples()))
            while True:
                if not self.deterministic:
                    random.shuffle(self.indexs)
                for index in self.indexs:
                    yield index

        for a_data in self._iterate(index_stream()):
            self.epoch = self.epoch + 1
            yield a_data

    # for testing
    def iterate_once(self):
        def index_stream():
            # yield data index
            self.indexs = list(range(self.get_num_examples()))
            for index in self.indexs:
                yield index

        for a_data in self._iterate(index_stream()):
            yield a_data


class TextConverter:

    @staticmethod
    def convert(txt_data, label_vocab, token_vocab):

        id_data = []

        for item in txt_data.data:
            label_id = label_vocab.get_id(item.label.strip())
            text_tokens = item.get_tokens()
            token_ids = [ token_vocab.get_id(token) for token in text_tokens ] # for each token
            #print(token_ids)
            new_item = copy.deepcopy(item)
            new_item.set_id(label_id,token_ids)
            id_data.append( new_item )

        return id_data