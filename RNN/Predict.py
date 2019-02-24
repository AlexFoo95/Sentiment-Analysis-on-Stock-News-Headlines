from tensorflow.core.framework import graph_pb2
import tensorflow as tf
import os
from TextPreprocessing import TextProcessing, TextConverter
from SentimentDataset import SentimentDataset


def predict(token_vocab, label_vocab, sent):  # mode = 'file' | 'sentence'
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # force to use cpu only (prediction)
    #model_dir = "./trained_models"
    # prepare sentence converting
    # to make raw sentence to id data easily
    in_sent = '{}\t{}'.format('___DUMMY_CLASS___', sent)
    pred_data = TextProcessing(in_sent, mode='sentence')
    pred_id_data = TextConverter.convert(pred_data, label_vocab, token_vocab)
    pred_data_set = SentimentDataset(pred_id_data, 1, 150)

    #
    a_batch_data = next(pred_data_set.predict_iterator)  # a result
    b_sentiment_id, b_token_ids, b_weight = a_batch_data

    # Restore graph
    # note that Frozen_graph.tf.pb contains graph definition with parameter values in binary format
    _graph_fn = ('E:\Pycharm Project\FYP\RNN\Frozen_graph.tf.pb')
    with tf.gfile.GFile(_graph_fn, "rb") as f:
        graph_def = tf.GraphDef()
        graph_def.ParseFromString(f.read())

    with tf.Graph().as_default() as graph:
        tf.import_graph_def(graph_def)

    with tf.Session(graph=graph) as sess:
        # to check load graph
        # for n in tf.get_default_graph().as_graph_def().node: print(n.name)

        # make interface for input
        pl_token = graph.get_tensor_by_name('import/model/pl_tokens:0')
        pl_keep_prob = graph.get_tensor_by_name('import/model/pl_keep_prob:0')

        # make interface for output
        out_pred = graph.get_tensor_by_name('import/model/out_pred:0')
        out_probs = graph.get_tensor_by_name('import/model/out_probs:0')

        # predict sentence
        b_best_pred_index, b_pred_probs = sess.run([out_pred, out_probs], feed_dict={
            pl_token: b_token_ids,
            pl_keep_prob: 1.0,
        }
                                                   )

        best_pred_index = b_best_pred_index[0]
        pred_probs = b_pred_probs[0]

        best_target_class = label_vocab.get_symbol(best_pred_index)
        print('Sentiment analysis result:', best_target_class, '   Predict_probability:', pred_probs[best_pred_index])

    return best_target_class, pred_probs[best_pred_index]