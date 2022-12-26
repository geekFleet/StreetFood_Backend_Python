import os
from multiprocessing.pool import ThreadPool
from azure.storage.blob import BlobServiceClient, BlobClient
from azure.storage.blob import ContentSettings, ContainerClient


CONNECTION_STRING = os.environ["AZUR_CONNECTION_STRING"]
CONTAINER_NAME = os.environ["CONTAINER_NAME"]
LOCAL_IMAGE_PATH = "profile-images/"


class AzureBlobFileUploader:
    def __init__(self):

        # Initialize the connection to Azure storage account
        self.blob_service_client = BlobServiceClient.from_connection_string(
            CONNECTION_STRING
        )

    def upload_all_images_in_folder(self):
        # Get all files with jpg extension and exclude directories
        all_file_names = [
            f
            for f in os.listdir(LOCAL_IMAGE_PATH)
            if os.path.isfile(os.path.join(LOCAL_IMAGE_PATH, f)) and ".jpg" in f
        ]

        result = self.run(all_file_names)

    def run(self, all_file_names):
        # Upload 10 files at a time!
        with ThreadPool(processes=int(10)) as pool:
            return pool.map(self.upload_image, all_file_names)

    def upload_image(self, file_name):
        # Create blob with same name as local file name
        blob_client = self.blob_service_client.get_blob_client(
            container=CONTAINER_NAME, blob=file_name
        )
        # Get full path to the file
        upload_file_path = os.path.join(LOCAL_IMAGE_PATH, file_name)

        # Create blob on storage
        # Overwrite if it already exists!
        image_content_setting = ContentSettings(
            content_type="image/jpeg", cache_control="max-age=3600"
        )
        with open(upload_file_path, "rb") as data:
            blob_client.upload_blob(
                data, overwrite=True, content_settings=image_content_setting
            )
            return file_name


# Initialize class and upload files
azure_blob_file_uploader = AzureBlobFileUploader()
