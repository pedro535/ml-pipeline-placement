#!/bin/bash

# 3 submissions
# 4 minutes between each submission

submission1=(
    "kddcup99/RF"
    "adult_income/DT"
    "credit_card/LR"
    "credit_card/SVM"
    "MNIST/NN"
    "CIFAR_10/CNN"
)

submission2=(
    "FASHION_MNIST/CNN"
    "wine_quality/DT"
    "kddcup99/SVM"
    "adult_income/LR"
    "UNSW_NB15/RF"
    "UNSW_NB15/SVM"
)

submission3=(
    "FASHION_MNIST/NN"
    "UNSW_NB15/SVM"
    "wine_quality/LR"
    "credit_card/DT"
    "citrus_leaves/CNN"
    "credit_card/RF"
)

echo "==== Submission 1 ===="
for pipeline in "${submission1[@]}"; do
    echo "==== Pipeline $pipeline ===="
    cd "$pipeline"
    # python pipeline.py
    sleep 0.4
    cd ../../
done

sleep 240

echo "==== Submission 2 ===="
for pipeline in "${submission2[@]}"; do
    echo "==== Pipeline $pipeline ===="
    cd "$pipeline"
    # python pipeline.py
    sleep 0.4
    cd ../../
done

sleep 240

echo "==== Submission 3 ===="
for pipeline in "${submission3[@]}"; do
    echo "==== Pipeline $pipeline ===="
    cd "$pipeline"
    # python pipeline.py
    sleep 0.4
    cd ../../
done