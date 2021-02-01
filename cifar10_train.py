# -*- coding:utf-8 -*-
import keras
import numpy as np
import os
import pandas as pd
import matplotlib

matplotlib.use('Agg') 
import matplotlib.pyplot as plt
from keras.optimizers import SGD
from keras.optimizers import Adam, Adadelta
from keras.callbacks import ModelCheckpoint, ReduceLROnPlateau
from keras import backend as K
from keras.datasets import cifar10
from keras.models import load_model
from data_input.data_input import getDataGenerator
from model.DenseNet import createSTNDenseNet

#define DenseNet params
ROWS = 32
COLS = 32
CHANNELS = 3
nb_classes = 7
batch_size = 32
nb_epoch = 100
img_dim = (ROWS,COLS,CHANNELS)
densenet_depth = 40
densenet_growth_rate = 12

#define filepath parms
check_point_file = r"./densenet_check_point_FER.h5"
loss_trend_graph_path = r"./fer-loss.jpg"
acc_trend_graph_path = r"./fer-acc.jpg"
resume = True
print('Now,we start compiling DenseNet model...')
model = createSTNDenseNet(nb_classes=nb_classes,img_dim=img_dim,depth=densenet_depth,
          growth_rate = densenet_growth_rate)
if resume == True:
    try: 
        model.load_weights(check_point_file)
    except:
        pass
optimizer = Adam()
#optimizer = SGD(lr=0.005)
#optimizer = Adadelta()
model.compile(loss='categorical_crossentropy',optimizer=optimizer,metrics=['accuracy'])

print('Now,we start loading data...')
#(x_train,y_train),(x_test,y_test) = cifar10.load_data()
'''
Loading FER Dataset:
'''
train = pd.read_csv("../input/fer.csv").values
test  = pd.read_csv("../input/fer.csv").values

trainX = train[:, 1:].reshape(train.shape[0],1,28, 28).astype( 'float32' )
X_train = trainX / 255.0
y_train = train[:,0]

testX = test[:,1:].reshape(test.shape[0],1, 28, 28).astype( 'float32' )
X_test = testX / 255.0
y_test = test[:,0]
#################################
x_train = X_train.astype('float32')
x_test = X_test.astype('float32')
#x_train /= 255
#x_test /= 255
y_train = keras.utils.to_categorical(y_train, nb_classes)
y_test= keras.utils.to_categorical(y_test, nb_classes)
train_datagen = getDataGenerator(train_phase=True)
train_datagen = train_datagen.flow(x_train,y_train,batch_size = batch_size)
validation_datagen = getDataGenerator(train_phase=False)
validation_datagen = validation_datagen.flow(x_test,y_test,batch_size = batch_size)
 
print('Now,we start defining callback functions...')
"""
lr_reducer = ReduceLROnPlateau(monitor='val_acc', factor=np.sqrt(0.1),
                            cooldown=0, patience=3, min_lr=1e-6)
"""
model_checkpoint = ModelCheckpoint(check_point_file, monitor="val_acc", save_best_only=True,
                          save_weights_only=True, verbose=1)
                         
#callbacks=[lr_reducer,model_checkpoint]
callbacks=[model_checkpoint]

print("Now,we start training...")
history = model.fit_generator(generator=train_datagen,
            steps_per_epoch= x_train.shape[0] // batch_size,
            epochs=nb_epoch,
            callbacks=callbacks,
            validation_data=validation_datagen,
            validation_steps = x_test.shape[0] // batch_size,
            verbose=1)

print("Now,we start drawing the loss and acc trends graph...")
#summarize history for accuracy 
fig = plt.figure(1)
plt.plot(history.history["acc"])  
plt.plot(history.history["val_acc"])  
plt.title("Model accuracy")  
plt.ylabel("accuracy")  
plt.xlabel("epoch")  
plt.legend(["train","test"],loc="upper left")  
plt.savefig(acc_trend_graph_path) 
plt.close(1)

#summarize history for loss
fig = plt.figure(2)     
plt.plot(history.history["loss"])  
plt.plot(history.history["val_loss"])  
plt.title("Model loss")  
plt.ylabel("loss")  
plt.xlabel("epoch")  
plt.legend(["train","test"],loc="upper left")  
plt.savefig(loss_trend_graph_path)
plt.close(2)
   
print("We are done, everything seems OK...")
    
