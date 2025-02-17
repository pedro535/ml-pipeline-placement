#!/bin/bash

option=$1
dataset_path=$2
base_dir="/mnt/datasets"
namespace="data-registry"
linked_pod=$(kubectl get pods -n $namespace --no-headers | awk '{print $1}')

if [ $option == "upload" ]; then
    echo "Uploading dataset $dataset_path to remote NFS Server..."
    kubectl cp $dataset_path $namespace/$linked_pod:$base_dir
    echo "Dataset uploaded successfully"
elif [ $option == "rm" ]; then
    echo "Removing dataset $dataset_path from remote NFS Server..."
    kubectl exec -n $namespace $linked_pod -- rm -rf $base_dir/$dataset_path
    echo "Dataset removed successfully"
else
    echo "Invalid option. Please use 'upload' or 'download'"
fi