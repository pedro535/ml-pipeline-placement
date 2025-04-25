#!/bin/bash

pipelines=(
    "UNSW_NB15/RF"
    "credit_card/LR"
    "CIFAR_10/CNN"
    "adult_income/LR"
    "adult_income/DT"
    "kddcup99/RF"
    "UNSW_NB15/SVM"
    "credit_card/DT"
    "kddcup99/SVM"
    "MNIST/NN"
)

for pipeline in "${pipelines[@]}"; do
    echo "==== Pipeline $pipeline ===="
    cd "$pipeline"
    python pipeline.py
    sleep 0.4
    cd ../../
done
