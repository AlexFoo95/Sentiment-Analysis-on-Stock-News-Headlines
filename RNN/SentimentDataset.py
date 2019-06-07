import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
import copy
from TextPreprocessing import Epoch, TextProcessing, TextConverter, Vocab
import numpy as np

class SentimentDataset(Epoch):
    def _iterate(self, index_gen):
        B = self.batch_size
        N = self.num_steps

        sentiment = np.zeros([B], np.int64)
        token = np.zeros([B, N], np.int64)
        weight = np.zeros([B, N], np.int64)

        while True:
            sentiment[:] = 0
            token[:] = 0
            weight[:] = 0

            for b in range(B):
                try:
                    while True:
                        index = next(index_gen)
                        _num_steps = len(self.data[index].token_ids)
                        if _num_steps <= N: break

                    _sentiment_id = copy.deepcopy(self.data[index].label_id)
                    _token_ids = copy.deepcopy(self.data[index].token_ids)


                    _weight_ids = [0] * self.num_steps
                    for _idx, _ in enumerate(_token_ids): _weight_ids[_idx] = 1


                    _token_ids += [self.token_pad_id] * (self.num_steps - len(_token_ids))

 
                    sentiment[b] = -1 if _sentiment_id is None else _sentiment_id

                    # input
                    token[b] = _token_ids
                    weight[b] = _weight_ids

                except StopIteration:
                    pass
            if not np.any(weight):
                return
            yield sentiment, token, weight


def load_data():

    token_vocab = Vocab(mode='token')
    label_vocab = Vocab(mode='label')
    train_txt_data = TextProcessing(mode = 'file')
    train_id_data = TextConverter.convert(train_txt_data, label_vocab, token_vocab)

    return train_id_data, token_vocab, label_vocab


def load_predict_info():
    token_vocab = Vocab(mode='token')
    label_vocab = Vocab(mode='label')

    return token_vocab, label_vocab