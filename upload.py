from pathlib import Path

from google.cloud import storage


def upload_blob(bucket_name, file_name):
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)
    blob = bucket.blob("data/" + file_name.name)

    blob.upload_from_filename(str(file_name))


if __name__ == "__main__":
    for fn in Path(".").glob("*jpg"):
        print("upload", fn.name)
        upload_blob("mfa-compute-demo", Path(fn.name))
