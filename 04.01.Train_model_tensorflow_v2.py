# -*- coding: utf-8 -*-
# @Time    : 2019/2/18 14:11
# @Author  : Avi
# @File    : Basic_Conv_Black.py
# @Software: PyCharm

import tensorflow as tf
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from sklearn.preprocessing import OneHotEncoder
import os
import glob
import sys
from sklearn.model_selection import train_test_split
import time
not_save = True
target_res = 0.96 #目标准确率
while not_save:
    # Loading dataset
    print("Loading dataset ...")
    
    images_per_batch = 10
    
    width = 480
    height = 180
    channel = 1
    classes = 7
    data = np.zeros((1, height, width))
    label = np.zeros((1, classes))
    deleted = 0
    total = 0
    image_array = np.zeros((1, height * width * channel))
    label_array = np.zeros((1, classes), 'float')
    training_data = glob.glob('dataset/*.npz')
    # i = 1
    if not training_data:
        print("No training data in directory, exit")
        sys.exit()
    
    for single_npz in training_data:
        with np.load(single_npz) as data:
            train_temp = data['train']
            train_labels_temp = data['train_labels']
        image_array = np.vstack((image_array, train_temp))
        label_array = np.vstack((label_array, train_labels_temp))
        # i += 1
    print("dataset loaded.")
    print("---------------------------------------------------------")
    X_data = image_array[1:, :]
    Y_data = label_array[1:, :classes]
    print ("X_data:", X_data.shape)
    print ("Y_data:", Y_data.shape)
    # print ("X_data:", X_data[:10, :])
    # print ("Y_data:", Y_data[:10, :])
    scaler = MinMaxScaler()
    X_data = np.reshape(X_data, (X_data.shape[0], height*width))
    X_data = scaler.fit_transform(X_data)
    
    print("X_data:", X_data.max(), X_data.min())
    # print ("Y_data:", Y[:10, :])
    
    trData, teData, trLabel, teLabel = train_test_split(X_data, Y_data, test_size=0.3)
    # 转换为图片的格式 （batch，height，width，channels）
    X = trData.reshape(-1, height, width, channel)
    Y = trLabel
    print('Y:', Y.shape)
    batch_size = 10 # 使用MBGD算法，设定batch_size为8
    
    
    def generatebatch(X, Y, n_examples, batch_size):
        for batch_i in range(n_examples // batch_size):
            start = batch_i * batch_size
            end = start + batch_size
            batch_xs = X[start:end]
            batch_ys = Y[start:end]
            yield batch_xs, batch_ys # 生成每一个batch
    
    
    tf.compat.v1.reset_default_graph()
    tf.compat.v1.disable_eager_execution()
    # 输入层
    tf_X = tf.compat.v1.placeholder(tf.float32, [None, height, width, channel], name='input') # 图像尺寸
    tf_Y = tf.compat.v1.placeholder(tf.float32, [None, classes])
    
    
    # 卷积层+激活层
    tf.compat.v1.disable_resource_variables()
    conv_filter_w1 = tf.compat.v1.get_variable('W', [5, 5, 1, 10], initializer=tf.compat.v1.keras.initializers.VarianceScaling(scale=1.0, mode="fan_avg", distribution="uniform")) #tf.Variable(tf.random_normal([3, 3, 1, 10]))
    conv_filter_b1 = tf.Variable(tf.random.normal([10]))
    relu_feature_maps1 = tf.nn.relu(tf.nn.conv2d(tf_X, filters=conv_filter_w1,strides=[1, 2, 2, 1], padding='SAME') + conv_filter_b1)
    print ("conv_out1:", relu_feature_maps1)
    # 池化层
    max_pool1 = tf.nn.max_pool2d(input=relu_feature_maps1,ksize=[1,3,3,1],strides=[1,2,2,1],padding='SAME')
    
    print ("max_pool:", max_pool1)
    
    
    # 卷积层
    conv_filter_w2 = tf.Variable(tf.random.normal([3, 3, 10, 5]))
    conv_filter_b2 =  tf.Variable(tf.random.normal([5]))
    conv_out2 = tf.nn.conv2d(max_pool1, filters=conv_filter_w2, strides=[1, 1, 1, 1], padding='SAME') + conv_filter_b2
    print ("conv_out2:", conv_out2)
    
    # BN归一化层+激活层
    batch_mean, batch_var = tf.nn.moments(conv_out2, [0, 1, 2], keepdims=True)
    shift = tf.Variable(tf.zeros([5]))
    scale = tf.Variable(tf.ones([5]))
    epsilon = 1e-3
    BN_out = tf.nn.batch_normalization(conv_out2, batch_mean, batch_var, shift, scale, epsilon)
    print("BN_out:", BN_out)
    relu_BN_maps2 = tf.nn.relu(BN_out)
    
    
    # 池化层
    max_pool2 = tf.nn.max_pool2d(input=relu_BN_maps2,ksize=[1,3,3,1],strides=[1,2,2,1],padding='SAME')
    print ("max_pool2", max_pool2)
    
    
    # 将特征图进行展开
    max_pool2_flat = tf.reshape(max_pool2, [-1, 23*60*5])
    
    # 全连接层
    fc_w1 = tf.Variable(tf.random.normal([23*60*5, 50]))
    fc_b1 = tf.Variable(tf.random.normal([50]))
    fc_out1 = tf.nn.relu(tf.matmul(max_pool2_flat, fc_w1) + fc_b1)
    
    dropout_keep_prob = 0.8
    fc1_drop = tf.nn.dropout(fc_out1, rate=1 - (dropout_keep_prob))
    
    # 输出层
    out_w1 = tf.Variable(tf.random.normal([50, classes]))
    out_b1 = tf.Variable(tf.random.normal([classes]))
    pred = tf.nn.softmax(tf.matmul(fc1_drop, out_w1) + out_b1, name='pred')
    
    loss = -tf.reduce_mean(tf_Y * tf.math.log(tf.clip_by_value(pred, 1e-11, 1.0)))
    train_step = tf.compat.v1.train.AdamOptimizer(3e-4, name='train_step').minimize(loss)
    
    y_pred = tf.argmax(pred, 1)
    bool_pred = tf.equal(tf.argmax(tf_Y,1),y_pred)
    
    accuracy = tf.reduce_mean(tf.cast(bool_pred,tf.float32), name="accuracy") # 准确率
    save_path = "model/auto_drive_model/"
    print("Start training ...")
    with tf.compat.v1.Session() as sess:
        sess.run(tf.compat.v1.global_variables_initializer())
        train_best = 0
        best_train_epoch = 0
        count = []
        test_res = 0
        test_best = 0
        best_test_epoch = 0
        for epoch in range(1000): # 迭代1000个周期
            print("*******************************************************************")
            for batch_xs,batch_ys in generatebatch(X,Y,Y.shape[0],batch_size): # 每个周期进行MBGD算法
                sess.run(train_step,feed_dict={tf_X:batch_xs,tf_Y:batch_ys})
            res = sess.run(accuracy,feed_dict={tf_X:X,tf_Y:Y})
            if res > train_best:
                train_best = res
                best_train_epoch = epoch
                # 执行预测
                Xte = teData.reshape((-1, height, width, channel))
                Yte = teLabel
                test_res = sess.run(accuracy, feed_dict={tf_X: Xte, tf_Y: Yte})
            if test_best < test_res:
                test_best = test_res
                best_test_epoch = epoch
                if test_res > target_res:
                    model = tf.compat.v1.train.Saver()
                    model.save(sess=sess, save_path=save_path, global_step=best_test_epoch)
                    print("已保存第", best_test_epoch, "步的训练结果")
                    time.sleep(5)
                    not_save = False
            print("Epoch:", epoch)
            print("Train res:", res,
                   ", best train accuracy is:",  train_best,
                   "at epoch:", best_train_epoch)
            print("Test res:", test_res,
                  ", best test accuracy is:", test_best,
                   "at epoch:", best_test_epoch)
            count = np.append(count, res)
            if len(count) >= 5:
                count = count[-5:]
                if np.var(count) < 1e-8:
                    break
    
        print("best result:", train_best, "best result in test:", test_best)
    
        sess.close()
    if not_save:
        print("训练失败，test_res(", test_res, ") < target_res(", target_res, ")，自动重新开始训练")
    
    
