from RNN import RNN
import tensorflow as tf
from SentimentDataset import SentimentDataset
from Graph import freeze_graph
import numpy as np

def train(train_id_data, num_vocabs, num_taget_class):

    max_epoch = 200
    model_dir = "E:\Pycharm Project\FYP\RNN\Trained_models\save_models.ckpt"
    hps = RNN.get_default_hparams()
    hps.update(
                    batch_size= 150,
                    num_steps = 120,
                    emb_size  = 100,
                    enc_dim   = 150,
                    vocab_size=num_vocabs + 1,
                    num_target_class=num_taget_class
               )

    with tf.variable_scope("model"):
        model = RNN(hps, "train")

    sv = tf.train.Supervisor(is_chief=True,logdir=model_dir,summary_op=None,global_step=model.global_step)

    # tf assign compatible operators for gpu and cpu
    tf_config = tf.ConfigProto(allow_soft_placement=True)

    with sv.managed_session(config=tf_config) as sess:
        local_step       = 0
        prev_global_step = sess.run(model.global_step)

        train_data_set = SentimentDataset(train_id_data, hps.batch_size, hps.num_steps)
        losses = []

        while not sv.should_stop():
            fetches = [model.global_step, model.loss, model.train_op]
            a_batch_data = next( train_data_set.iterator )
            y, x, w = a_batch_data
            fetched = sess.run(fetches, {
                                            model.x: x,
                                            model.y: y,
                                            model.w: w,
                                            model.keep_prob: hps.keep_prob
                                        }
                              )

            local_step += 1
            _global_step = fetched[0]
            _loss        = fetched[1]
            losses.append( _loss )
            if local_step < 10 or local_step % 10 == 0:
                epoch = train_data_set.get_epoch_num()
                print("Epoch = {:3d} Step = {:7d} loss = {:5.3f}".format(epoch, _global_step, np.mean(losses)) )
                _loss = []
                if epoch >= max_epoch : break

        print("Training is done.")
    sv.stop()

    # model.out_pred, model.out_probs
    freeze_graph(model_dir, "model/out_pred,model/out_probs", "Final_graph.tf.pb") ## freeze graph with params to probobuf format

