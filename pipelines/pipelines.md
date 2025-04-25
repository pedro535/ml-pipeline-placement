# Pipelines to run

## Single time window (stress test)

- 10 pipelines
    - 2 LR
    - 2 DT
    - 2 RF
    - 2 SVM
    - 1 NN
    - 1 CNN

## Multiple time windows
Total windows: 4
Time between submissions: 3 minutes

Time window 1:
- 5 pipelines
    - 1 LR
    - 1 DT
    - 1 RF
    - 1 SVM
    - 1 NN
    - 1 CNN

Time window 2:
- 5 pipelines
    - 1 LR
    - 1 DT
    - 1 RF
    - 1 SVM
    - 1 NN
    - 1 CNN

Time window 3:
- 5 pipelines
    - 1 LR
    - 1 DT
    - 1 RF
    - 1 SVM
    - 1 NN
    - 1 CNN


## Pipelines needed of each type

LR: 2
- adult income
- (thyroid/diabetes/heart disease | wine quality)
- (credit card default)

DT: 4
- adult income
- (thyroid/diabetes/heart disease | wine quality)
- (credit card default)

RF: 4
- kddcup99
- UNSWN-NB15
- (Credit Card Default)

SVM: 4
- kddcup99
- UNSWN-NB15
- (Credit Card Default)

NN: 2
- UNSWN-NB15
- MNIST
- FASHION-MNIST

CNN: 2
- CIFAR-10
- MNIST
- FASHION-MNIST
