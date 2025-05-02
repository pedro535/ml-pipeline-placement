#!/bin/bash

pipelines=(
    "unsw_nb15_rf"
    "credit_card_lr"
    "cifar10_cnn"
    "adult_income_lr"
    "adult_income_dt"
    "kddcup99_rf"
    "unsw_nb15_svm"
    "credit_card_dt"
    "kddcup99_svm"
    "mnist_nn"
)

for pipeline in "${pipelines[@]}"; do
    echo "==== Pipeline $pipeline ===="
    cd "$pipeline"
    python kfp_pipeline.py
    sleep 0.5
    cd ..
    echo "\n"
done
