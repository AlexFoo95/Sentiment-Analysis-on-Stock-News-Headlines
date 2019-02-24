from SentimentDataset import load_data
from TrainData import train

if __name__ == '__main__':
    train_id_data, token_vocab, target_vocab = load_data()
    num_vocabs = token_vocab.get_num_tokens()  # Vocab.get_num_tokens()
    num_target_class = target_vocab.get_num_targets()  # Vocab.get_num_targets()
    train(train_id_data, num_vocabs, num_target_class)