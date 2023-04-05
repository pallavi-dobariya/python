from tensorflow.keras.layers import Input, Lambda, Dense, Flatten
from tensorflow.keras.models import Model
from tensorflow.keras.applications.inception_v3 import InceptionV3
#from keras.applications.vgg16 import VGG16
from tensorflow.keras.applications.inception_v3 import preprocess_input
from tensorflow.keras.preprocessing import image
from tensorflow.keras.preprocessing.image import ImageDataGenerator,load_img
#from tensorflow.keras.models import Sequential
import numpy as np
from glob import glob
import splitfolders
import tensorflow as tf
from keras.models import load_model
import cv2
from sklearn.metrics import classification_report, confusion_matrix,accuracy_score
from tensorflow.python.estimator import keras
from keras.callbacks import EarlyStopping
from livelossplot import PlotLossesKeras
import matplotlib.pyplot as plt

IMAGE_SIZE = [224, 224]
image_size =500
batch_size = 40
epoc =50

splitfolders.ratio('C:\\Users\\kc\\Desktop\\Nutrient_deficiency_Pycharm\\dataset_new', output="output", seed=1337, ratio=(.8, 0.1,0.1))


train_dir = "C:\\Users\\kc\\Desktop\\Nutrient_deficiency_Pycharm\\output\\train"
val_dir = "C:\\Users\\kc\\Desktop\\Nutrient_deficiency_Pycharm\\output\\val"
test_dir = "C:\\Users\\kc\\Desktop\\Nutrient_deficiency_Pycharm\\output\\test"

datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
train_generator = datagen.flow_from_directory(train_dir,target_size=(224,224),
                                              batch_size=batch_size,
                                              seed=142,
                                              shuffle=True)
val_generator = datagen.flow_from_directory(val_dir,target_size=(224,224),
                                              batch_size=batch_size,
                                              seed=142)

inception = InceptionV3(input_shape=IMAGE_SIZE + [3], weights='imagenet', include_top=False)

for layer in inception.layers:
    layer.trainable = False
folders = glob('C:/Users/kc/Desktop/Nutrient_deficiency_Pycharm/output/train/*')
print(folders)
x = Flatten()(inception.output)

prediction = Dense(len(folders), activation='softmax')(x)

model = Model(inputs=inception.input, outputs=prediction)

model.summary()

model.compile(
  loss='categorical_crossentropy',
  optimizer='adam',
  metrics=['accuracy']
)

monitor_val_acc = EarlyStopping(monitor = 'val_loss', patience = 5)

history = model.fit(
  train_generator,
  validation_data=val_generator,
  epochs=epoc,
  steps_per_epoch=len(train_generator),
  validation_steps=len(val_generator),
  callbacks=[PlotLossesKeras(), monitor_val_acc]
)

model.save('model.h5')
history.history.keys()

fig=plt.figure(1)
fig.subplots_adjust(hspace=0.6)
# summarize history for accuracy
plt.subplot(211)
plt.plot(history.history['accuracy'])
plt.plot(history.history['val_accuracy'])
plt.title('model accuracy')
plt.ylabel('accuracy')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='lower right')

# summarize history for loss


plt.subplot(212)
plt.plot(history.history['loss'])
plt.plot(history.history['val_loss'])
plt.title('model loss')
plt.ylabel('loss')
plt.xlabel('epoch')
plt.legend(['train', 'test'], loc='upper right')

plt.show()

testdatagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
test_generator = testdatagen.flow_from_directory(
    test_dir,
    target_size=(224, 224),
    batch_size=batch_size,
    shuffle=False)

predict = model.predict(test_generator,steps = len(test_generator),verbose=1)

predicted_class_indices=np.argmax(predict,axis=1)
labels=(test_generator.class_indices)
labels2=dict((v,k) for k,v in labels.items())
predictions=[labels2[k] for k in predicted_class_indices]
Y_pred = predict
y_pred = np.argmax(Y_pred, axis=1)

print('Confusion Matrix')
cf_matrix=confusion_matrix(test_generator.classes, y_pred)
print(cf_matrix)

print('\n Classification Report')
target_names = ['calcium_deficiency','healthy','nitrogen_deficiency','potassium_deficiency']
print(classification_report(test_generator.classes, y_pred, target_names=target_names))

testacc=accuracy_score(test_generator.classes, y_pred, normalize=True)
print(testacc)


model = load_model('model.h5')
model.compile(loss='categorical_crossentropy',
  optimizer='adam',
  metrics=['accuracy']
)
img = cv2.imread('C:\\Users\\kc\\Desktop\\Nutrient_deficiency_Pycharm\\dataset_new\\nitrogen_deficiency\\16.jpg')
img = cv2.resize(img, (224,224))
img = np.reshape(img,[1,224,224,3])
classes = model.predict(img)
print(classes)