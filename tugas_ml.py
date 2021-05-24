# -*- coding: utf-8 -*-
"""Tugas ML.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1J2O_gxdWHZ_qE9YK1JSoXh33XgD35zpJ

### Tugas *Image Classification* Kelas Reguler A
M. Verdy Rizaldi N. (18/427585/PA/18545)

Thariq Izkandar Z.M.P. (18/424198/PA/18303)

Ivan Liu Nardo S. (18/427581/PA/18541)

## 0. Import library yang digunakan
"""

import numpy as np
import os
import random
import cv2
import matplotlib.pyplot as plt

"""## 1. Tentukan Arsitektur MLP
Pada tugas, dideskripsikan bahwa:
- input adalah gambar dengan resolusi 320x240.
- hanya menggunakan 1 hidden layer

Sehingga, dengan *requirement* tersebut, kami mengkonstruksikan arsitektur seperti berikut:
1. input layer dengan jumlah neuron 320*240 = 76800
2. hidden layer dengan jumlah neuron 50
3. output layer dengan jumlah neuron 3, dimana digunakan one-hot encoding dengan format [sunflower, daisy, dandelion]

## 2. Definisikan arsitektur yang digunakan
"""

# inisialisasikan variabel untuk theta
INPUT_LAYER_NEURON = 76800
HIDDEN_LAYER_NEURON = 50
OUTPUT_LAYER_NEURON = 3

class MultiLayeredPerceptronWeights:
  def __init__(self):
    # theta antara layer input-hidden
    self.theta_input_hidden = np.empty([INPUT_LAYER_NEURON, HIDDEN_LAYER_NEURON])
    self.bias_input_hidden = np.empty(HIDDEN_LAYER_NEURON)
    # theta antara layer hidden-output
    self.theta_hidden_output = np.empty([HIDDEN_LAYER_NEURON, OUTPUT_LAYER_NEURON])
    self.bias_hidden_output = np.empty(OUTPUT_LAYER_NEURON)

"""## 3. Definisikan fungsi Load dataset dan visualisasi data"""

# definisikan fungsi untuk parsing dataset dari folder
def parse_dataset(folder_path):
  dataset = []
  for label in os.listdir(folder_path):
    label_path = os.path.join(folder_path, label)
    for data in os.listdir(label_path):
      data_path = os.path.join(label_path, data)
      # encode label dengan menggunakan one-hot-encoding
      if label == 'sunflower':
        label_encoded = np.array([1, 0, 0])
      elif label == 'daisy':
        label_encoded = np.array([0, 1, 0])
      else:
        label_encoded = np.array([0, 0, 1])
      dataset.append((label_encoded, data_path))
  return dataset

# parse dataset training dan testing
train_dataset_paths = parse_dataset('training')
test_dataset_paths = parse_dataset('testing')

# shuffle data untuk menghindari bias pada training
random.shuffle(train_dataset_paths)
random.shuffle(test_dataset_paths)

# visualisasikan beberapa dataset
for label, data_path in train_dataset_paths[:10]:
  data = cv2.resize(cv2.imread(data_path), (320, 240))
  cv2.imshow(data)
  print(label, '\n')

"""## 4. Definisikan fungsi grayscale dan preprocessing lainnya"""

def preprocess(img):
  # lakukan preprocessing pada gambar
  # resize ke 320x240
  proc = cv2.resize(img, (320, 240))
  # ubah ke grayscale
  proc = cv2.cvtColor(proc, cv2.COLOR_BGR2GRAY)
  # ubah gambar ke 1 dimensi
  proc = proc.flatten()
  return proc

# lakukan preprocessing pada dataset
train_dataset = [(label, preprocess(cv2.imread(img_path))) for label, img_path in train_dataset_paths]
test_dataset = [(label, preprocess(cv2.imread(img_path))) for label, img_path in test_dataset_paths]

"""## 5. Definisikan fungsi aktivasi sigmoid"""

import numpy as np

def sigmoid(x):
  return 1/(1 + np.exp(-x))

"""## 6. Definisikan  fungsi algoritma pembelajaran backpropagation - Inisialisasi bobot and bias"""

def initialize(model):
  # inisialisasi bobot dan bias menggunakan He initialization
  # setiap bobot diinisialisasi menggunakan generator random gaussian
  # dengan mean 0 dan variance sqrt(2/n)
  # random initialization digunakan untuk mendapatkan delta bobot yang baik pada hidden layer
  # theta antara layer input-hidden
  model.theta_input_hidden = np.random.normal(0, 2/INPUT_LAYER_NEURON, (INPUT_LAYER_NEURON, HIDDEN_LAYER_NEURON))
  model.bias_input_hidden = np.random.normal(0, 2/INPUT_LAYER_NEURON, HIDDEN_LAYER_NEURON)
  # theta antara layer hidden-output
  model.theta_hidden_output = np.random.normal(0, 2/HIDDEN_LAYER_NEURON, (HIDDEN_LAYER_NEURON, OUTPUT_LAYER_NEURON))
  model.bias_hidden_output = np.random.normal(0, 2/HIDDEN_LAYER_NEURON, OUTPUT_LAYER_NEURON)

"""## 7. Definisikan fungsi algoritma pembelajaran backpropagation - menghitung error"""

def calc_err(label, output):
  return  ((output - label)**2)/2

"""## 8. Definisikan fungsi algoritma pembelajaran backpropagation - Feedforward"""

def calc_output(input, model):
  hidden_y = sigmoid(np.dot(input, model.theta_input_hidden) + model.bias_input_hidden)
  output_y = sigmoid(np.dot(hidden_y, model.theta_hidden_output) + model.bias_hidden_output)

  # luaran hidden layer juga di-return untuk menghitung dtheta nantinya
  return output_y, hidden_y

"""## 9. Definisikan fungsi algoritma pembelajaran backpropagation - backward (update bobot)"""

def update_weight(label, input, model, learning_rate):
  output_y, hidden_y = calc_output(input, model)
  
  # reshape dan transpose matriks agar dapat dicari dot productnya
  hidden_y = hidden_y.reshape((len(hidden_y), 1))
  output_y = output_y.reshape((1, len(output_y)))
  input_reshaped = input.reshape((len(input), 1))

  # hitung error
  output_error = calc_err(label, output_y)

  # hitung dtheta hidden-output
  derivative_hidden_output = (output_y - label) * output_y * (1 - output_y)
  dtheta_hidden_output = np.dot(hidden_y, derivative_hidden_output)
  
  # hitung dtheta input-hidden
  hidden_error = np.dot(model.theta_hidden_output, derivative_hidden_output.T)
  derivative_input_hidden = hidden_error * hidden_y * (1 - hidden_y)
  derivative_input_hidden = derivative_input_hidden.reshape((1, len(derivative_input_hidden)))
  dtheta_input_hidden = np.dot(input_reshaped, derivative_input_hidden)

  # update theta
  model.theta_hidden_output -= learning_rate * dtheta_hidden_output / len(train_dataset)
  model.bias_hidden_output -= learning_rate * derivative_hidden_output[0] / len(train_dataset)
  model.theta_input_hidden -= learning_rate * dtheta_input_hidden / len(train_dataset)
  model.bias_input_hidden -= learning_rate * derivative_input_hidden[0] / len(train_dataset)

  # return total error baru
  return np.sum(calc_err(label, calc_output(input, model)[0]))

"""## 10. Definisikan fungsi algoritma pembelajaran backpropagation - prediksi"""

def predict(input, model):
  output, _ = calc_output(input, model)
  # ambil index hipotesis dengan probabilitas paling tinggi
  return np.argmax(output)

"""## 11. Definisikan fungsi algoritma pembelajaran backpropagation - mendefinisikan fungsi akurasi"""

def calc_accuracy(model):
  correct_count = 0
  for label, data in test_dataset:
    if np.argmax(label) == predict(data, model):
      correct_count += 1
  return correct_count / len(test_dataset)

"""## 12. Definisikan fungsi training (80% data) dan testing (20% data)"""

def train(model, epoch, learning_rate):
  print("\n\nTraining model; epoch =", epoch, "; learning_rate =", learning_rate)
  errors = []
  accuracies = []
  prev_log_string = ''
  for cur_epoch in range(epoch):
    total_error = 0
    for data_index, (label, data) in enumerate(train_dataset):
      cur_error = update_weight(label, data, model, learning_rate)
      total_error += cur_error
      # log progress training
      # agar log tetap di line yang sama, hapus log sebelumnya
      print('\b' * len(prev_log_string), end='')
      # log progress yang sekarang
      prev_log_string = f'EPOCH {cur_epoch + 1}/{epoch}, DATA {data_index}/{len(train_dataset)}'
      if len(errors) > 0:
        prev_log_string += f', MODEL_ERROR: {errors[-1]}'
      print(prev_log_string, end='')
    errors.append(total_error/len(train_dataset))
    #print(total_error/len(train_dataset))
    accuracies.append(calc_accuracy(model))
  print("TRAINING FINISHED")
  return errors, accuracies

"""## 13. Visualisasikan error dan akurasi setiap epoch untuk 50 epoch, dan coba gunakan learning rate = 0,1 ; learning rate = 0,8"""

# definisikan fungsi untuk memvisulisasikan error dan akurasi
def visualize(errors, accuracies):
  plt.title("Errors / Loss")
  plt.plot(errors, 'r-')
  plt.show()
  plt.title("Accuracy")
  plt.plot(accuracies, 'b-')
  plt.show()
 
# percobaan epoch=50 dan learning rate=0,1
model_0_1 = MultiLayeredPerceptronWeights()
initialize(model_0_1)
errors_0_1, accuracies_0_1 = train(model_0_1, 50, 0.1)
visualize(errors_0_1, accuracies_0_1)
 
# percobaan epoch=50 dan learning rate=0,8
model_0_8 = MultiLayeredPerceptronWeights()
initialize(model_0_8)
errors_0_8, accuracies_0_8 = train(model_0_1, 50, 0.8)
visualize(errors_0_8, accuracies_0_8)
