#!/bin/bash

# ADULT INCOME
cd adult_income/

cd LR
python pipeline.py
sleep 0.5
cd ..

cd DT
python pipeline.py
sleep 0.5
cd ..

cd RF
python pipeline.py
sleep 0.5
cd ../../


# CIFAR-10
cd CIFAR_10

cd NN1
python pipeline.py
sleep 0.5
# cd ..

# cd NN2
# python pipeline.py
# sleep 0.5
cd ../../

# KDDCUP99
cd kddcup99

cd RF
python pipeline.py
sleep 0.5
cd ..

cd SVM
python pipeline.py
sleep 0.5
cd ../../


# MNIST
cd MNIST

# cd LR
# python pipeline.py
# sleep 0.5
# cd ..

cd NN1
python pipeline.py
sleep 0.5
# cd ..

# cd NN2
# python pipeline.py
# sleep 0.5
cd ../../


# UNSW_NB15
cd UNSW_NB15

# cd NN
# python pipeline.py
# sleep 0.5
# cd ..

# cd RF
# python pipeline.py
# sleep 0.5
# cd ..

cd SVM
python pipeline.py
sleep 0.5
cd ../../