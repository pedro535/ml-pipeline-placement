#!/bin/bash

server_ip="10.255.32.122"
server_user="atnoguser"
base_dir="/mnt/datasets"

option=$1
dataset_path=$2
dataset_name=$(basename $dataset_path)
datasets_dir=$(dirname $dataset_path)


function upload {
    echo "Uploading dataset to remote NFS Server..."
    scp -r $datasets_dir/$dataset_name.zip $server_user@$server_ip:/tmp

    echo "Unzipping dataset..."
    ssh $server_user@$server_ip "sudo unzip /tmp/$dataset_name.zip -d $base_dir; sudo rm /tmp/$dataset_name.zip"

    echo "Dataset uploaded successfully"
    rm $datasets_dir/$dataset_name.zip
}

function remove {
    echo "Removing dataset $dataset_path from remote NFS Server..."
    ssh $server_user@$server_ip "sudo rm -rf $base_dir/$dataset_name"
    echo "Dataset removed successfully"
}

function zip_dataset {
    echo "Zipping dataset $dataset_path..."
    cd $datasets_dir
    zip -r $dataset_name.zip $dataset_name
    echo "Dataset zipped successfully"
    cd ..
}

function delete_hidden_files {
    find $dataset_path -name ".*" -exec rm -rf {} \;
    echo "Hidden files deleted successfully"
}


if [ $option == "upload" ]; then
    delete_hidden_files
    zip_dataset
    upload
elif [ $option == "rm" ]; then
    remove
else
    echo "Invalid option. Please use 'upload' or 'download'"
fi