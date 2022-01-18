import os

import requests
from google.cloud import storage


def create_import_job(event, context):
    """Background Cloud Function to be triggered by Cloud Storage.
       This generic function logs relevant data when a file is changed.
    Args:
        event (dict):  The dictionary with data specific to this type of event.
                       The `data` field contains a description of the event in
                       the Cloud Storage `object` format described here:
                       https://cloud.google.com/storage/docs/json_api/v1/objects#resource
        context (google.cloud.functions.Context): Metadata of triggering event.
    Returns:
        None; the output is written to Stackdriver Logging
    """

    api_url = os.environ['API_URL']
    api_token = os.environ['API_TOKEN']

    input_folder = os.environ['INPUT_FOLDER']
    processed_folder = os.environ['PROCESSED_FOLDER']

    bucket, file_name = event['bucket'], event['name']
    if file_name.startswith(processed_folder) or not file_name.startswith(input_folder):
        return

    client = storage.Client()

    client_bucket = client.bucket(bucket)
    blob = client_bucket.get_blob(file_name)
    file_content = blob.download_as_bytes(raw_download=True)

    headers = {
        'Authorization': f'Token {api_token}',
        'Content-Type': event['contentType']
    }

    response = requests.post(api_url, data=file_content, headers=headers)
    if response.status_code == 202:
        processed_file_name = file_name.replace(input_folder, processed_folder)
        client_bucket.rename_blob(blob, new_name=processed_file_name)
    else:
        print(response.status_code)
        print(response.content)
        raise Exception("Failed to create import job")
