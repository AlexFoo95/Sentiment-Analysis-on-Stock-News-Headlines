import tensorflow as tf
from tensorflow.contrib.layers.python.layers import linear
from HParam import HParams

class RNN():
    def __init__(self, hps, mode="train"):

        #--- initialise of the variables
        self.hps = hps
        self.x = tf.placeholder(tf.int32, [None, hps.num_steps], name="pl_tokens")
        self.y = tf.placeholder(tf.int32, [None], name="pl_target")
        self.w = tf.placeholder(tf.float32, [None, hps.num_steps], name="pl_weight")
        self.keep_prob = tf.placeholder(tf.float32, [], name="pl_keep_prob")

        #--- the embedding layer of the RNN
        def _embedding(x, keep_prob):
            shape = [hps.vocab_size, hps.emb_size]
            initializer = tf.initializers.variance_scaling(distribution="uniform", dtype=tf.float32)
            emb_mat = tf.get_variable("emb", shape, initializer=initializer, dtype=tf.float32)
            input_emb = tf.nn.embedding_lookup(emb_mat, x)  # [batch_size, sent_len, emb_dim]
            step_inputs = tf.unstack(input_emb, axis=1)

            with tf.name_scope('sequence_dropout') as scope:
                step_outputs = []
                for t, input in enumerate(step_inputs):
                    step_outputs.append(tf.nn.dropout(input, keep_prob))
            return step_outputs

        #--- the hidden layer of the rnn
        def sequence_encoding_n21_rnn(step_inputs, cell_size, scope_name):
            # rnn based N21 encoding (GRU)
            step_inputs = list(reversed(step_inputs))
            f_rnn_cell = tf.contrib.rnn.GRUCell(cell_size, reuse=None)
            _inputs = tf.stack(step_inputs, axis=1)
            step_outputs, final_state = tf.contrib.rnn.static_rnn(f_rnn_cell,step_inputs,dtype=tf.float32,scope=scope_name)
            out = step_outputs[-1]
            return out

        def _to_class(input, num_class):
            out = linear(input, num_class, scope="Rnn2Sentiment")
            return out

        #--- the output layer of the rnn
        def _loss(out, ref):
            batch_loss = tf.nn.sparse_softmax_cross_entropy_with_logits(logits=out, labels=ref, name="sentiment_loss")
            loss = tf.reduce_mean(batch_loss)
            return loss

        seq_length = tf.reduce_sum(self.w, 1)  # [batch_size]

        #--- call the above function
        #--- call the embedding layer
        step_inputs = _embedding(self.x, self.keep_prob)
        #--- the step_inputs will be pass to hidden layer and process
        sent_encoding = sequence_encoding_n21_rnn(step_inputs, hps.enc_dim, scope_name="encoder")
        out = _to_class(sent_encoding, hps.num_target_class)
        loss = _loss(out, self.y)

        #--- produce the accuracy of the prediction
        out_probs = tf.nn.softmax(out, name="out_probs")
        #--- produce the polarity of the prediction
        out_pred = tf.argmax(out_probs, 1, name="out_pred")

        self.loss = loss
        self.out_probs = out_probs
        self.out_pred = out_pred

        self.global_step = tf.get_variable("global_step", [], tf.int32, initializer=tf.zeros_initializer,trainable=False)

        if mode == "train":
            optimizer = tf.train.AdamOptimizer(hps.learning_rate)
            self.train_op = optimizer.minimize(self.loss, global_step=self.global_step)
        else:
            self.train_op = tf.no_op()

    @staticmethod
    def get_default_hparams():
        return HParams(
            learning_rate=0.001,
            keep_prob=0.5,
        )