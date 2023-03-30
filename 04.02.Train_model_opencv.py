import cv2
import numpy as np
import glob
import sys
from sklearn.model_selection import train_test_split

print('Loading training data...')
e0 = cv2.getTickCount()

# load training data:
img_w = 480
img_h = 180
img_c = 1
image_array = np.zeros((1, img_h * img_w * img_c))
label_array = np.zeros((1, 7), 'float')
training_data = glob.glob('dataset/*.npz')

# if no data, exit
if not training_data:
    print("No training data in directory, exit")
    sys.exit()

for single_npz in training_data:
    with np.load(single_npz) as data:
        train_temp = data['train']
        train_labels_temp = data['train_labels']
        # if train_labels_temp.shape[1] == 4:
        #     tmp = np.zeros((train_labels_temp.shape[0], 2), 'float')
        #     train_labels_temp = np.hstack((train_labels_temp, tmp))
        # elif train_labels_temp.shape[1] ==6:
        #     for one_label in train_labels_temp:
        #         print("one label:", one_label)
        #         if one_label[4] == 1:
        #             train_labels_temp[1] = 1
        #
        #         elif one_label[5] == 1:
        #             train_labels_temp[0] = 1
        #
        #         one_label=np.array(one_label).reshape((1, 6))
        #         print("first:", one_label)
        #         np.delete(one_label)
        #         print(one_label.shape)
    image_array = np.vstack((image_array, train_temp))
    label_array = np.vstack((label_array, train_labels_temp))

X = image_array[1:, :]
y = label_array[1:, :7]
print("y:", y.shape)
print('Image array shape: ', X.shape)
print('x.max:', np.amax(X))
print('x.min:', np.amin(X))
print('Label array shape: ', y.shape)
# print('y:', y[:150])

e00 = cv2.getTickCount()
time0 = (e00 - e0) / cv2.getTickFrequency()
print('Loading image duration:', time0)

# train test split, 7:3
train, test, train_labels, test_labels = train_test_split(X, y, test_size=0.2)
print("train.shape", train.shape)
# set start time
e1 = cv2.getTickCount()

# create MLP
layer_sizes = np.int32([img_w * img_h * img_c, 16,  y.shape[1]])
model = cv2.ml.ANN_MLP_create()
# model = cv2.ml.ANN_MLP_load('mlp_xml/mlp(left_right_basic).xml')
model.setLayerSizes(layer_sizes)
model.setActivationFunction(cv2.ml.ANN_MLP_SIGMOID_SYM)
criteria = (cv2.TERM_CRITERIA_COUNT | cv2.TERM_CRITERIA_EPS, 375, 0.001)
model.setTermCriteria(criteria)
model.setTrainMethod(cv2.ml.ANN_MLP_BACKPROP)

print('Training MLP ...')
# num_iter = model.train(train, train_labels, None, params = params)
model.train(np.array(X, dtype=np.float32),
            cv2.ml.ROW_SAMPLE,
            np.array(y, dtype=np.float32))

# set end time
e2 = cv2.getTickCount()
time = (e2 - e1)/cv2.getTickFrequency()
print('Training duration:', time)
print()
#print 'Ran for %d iterations' % num_iter

# train data
ret_0, resp_0 = model.predict(train)
# print('resp:', resp_0)
prediction_0 = resp_0.argmax(-1)
print("prediction:", prediction_0[:100])
true_labels_0 = train_labels.argmax(-1)

train_rate = np.mean(prediction_0 == true_labels_0)
print('Train accuracy: ', "{0:.2f}%".format(train_rate * 100))


# test data
ret_1, resp_1 = model.predict(test)
prediction_1 = resp_1.argmax(-1)
true_labels_1 = test_labels.argmax(-1)

test_rate = np.mean(prediction_1 == true_labels_1)
print('Test accuracy: ', "{0:.2f}%".format(test_rate * 100))
# cv2.ml_ANN_MLP.isTrained()
# save model
model.save('mlp_xml/mlp.xml')
