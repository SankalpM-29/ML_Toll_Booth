import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage

# bucket_name = "toll-booth-6d3c9"
# source_blob_name = "car.jpg"
# destination_file_name = "./car.jpg"

def download_image_from_fb(bucket_name, source_blob_name, destination_file_name):
    cred = credentials.Certificate('./toll-booth.json')
    firebase_admin.initialize_app(cred, {'storageBucket': f'{bucket_name}.appspot.com'})

    bucket = storage.bucket()

    blob = bucket.blob(source_blob_name)
    blob.download_to_filename(destination_file_name)

    print("Downloaded storage object {} from bucket {} to local file {}.".format(source_blob_name, bucket_name, destination_file_name))
