import os
from dotenv import load_dotenv
import argparse
from minio import Minio


load_dotenv()
ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
SECRET_KEY = os.getenv("MINIO_SECRET_KEY")
MINIO_URL = os.getenv("MINIO_URL")

parser = argparse.ArgumentParser()
parser.add_argument("-c", help="Create a new bucket")
parser.add_argument("-r", help="Remove bucket")
parser.add_argument("-l", action="store_true", help="List all buckets")
parser.add_argument("-o", help="List all objects in a bucket")
parser.add_argument("--file", nargs=3, help="Upload a file to a bucket: [bucket_name] [path] [obj_name_with_prefix]")
parser.add_argument("--folder", nargs=3, help="Upload an entire folder to a bucket: [bucket_name] [path]")

args = parser.parse_args()


def bucket_objects(client, bucket):
    return [obj.object_name for obj in client.list_objects(bucket, recursive=True)]


def create_bucket(client, bucket):
    client.make_bucket(bucket)
    print(f"Bucket '{bucket}' created")


def remove_bucket(client, bucket):
    # empty bucket
    for obj in bucket_objects(client, bucket):
        client.remove_object(bucket, obj)

    client.remove_bucket(bucket)
    print(f"Bucket '{bucket}' removed")


def list_buckets(client):
    buckets = client.list_buckets()
    for b in buckets:
        print(b.name)


def list_objects(client, bucket):
    objects = bucket_objects(client, bucket)
    for obj in objects:
        print(obj)


def upload_file(client, bucket, path, name):
    client.fput_object(bucket, name, path)
    print(f"File '{name}' uploaded to bucket '{bucket}'")


def upload_folder(client, bucket, path):
    print("folder")
    

if __name__ == "__main__":
    client = Minio(
        endpoint = MINIO_URL,
        access_key = ACCESS_KEY, 
        secret_key = SECRET_KEY,
        secure=False
    )

    if args.c:
        create_bucket(client, args.c)
    elif args.r:
        remove_bucket(client, args.r)
    elif args.l:
        list_buckets(client)
    elif args.o:
        list_objects(client, args.o)
    elif args.file:
        upload_file(client, args.file[0], args.file[1], args.file[2])
    elif args.folder:
        upload_folder(client, args.folder[0], args.folder[1])
    else:
        print("Invalid arguments")