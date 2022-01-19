import os
import json
from pathlib import Path

import requests
from google.cloud.storage import Client as StorageClient


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

    """
    
    Library structure:
    
    - src
    - tests
    - examples
      - google_cloud/bucket_cloud_function
    
    from goalplan.google import BucketFileImporter
    
    client = BucketFileImporter(base_url, api_token, file_mappings)

    or

    client = BucketFileImporter.from_config_file(file_path_to_json_config, **config_overrides)
    client.handle(bucket, filepath, dry_run=True/False)
    """

    config_path = Path(__file__).with_name('config.json')
    with open(config_path) as f:
        config = json.load(f)

    api_token = config['api_token']
    api_base_url = config['base_url']
    import_jobs_mapping = config['import_jobs_mapping']

    bucket, file_path = event['bucket'], event['name']
    file_folder, file_name = file_path.rsplit('/', maxsplit=1)

    for folder, definition_id in import_jobs_mapping.items():
        if folder == file_folder:
            matched_definition_id = definition_id
            print(f"Matched file {file_path}. Using configured definition id {definition_id}.")
            break
    else:
        print(f"Ignoring file {file_path}. No match found in configured import_jobs_mapping.")
        return

    client = StorageClient()

    client_bucket = client.bucket(bucket)
    blob = client_bucket.get_blob(file_path)
    file_content = blob.download_as_bytes(raw_download=True)

    headers = {
        'Authorization': f'Token {api_token}',
        'Content-Type': event['contentType']
    }
    data_url = api_base_url + matched_definition_id

    response = requests.post(data_url, data=file_content, headers=headers)
    if response.status_code == 202:
        import_job_url = response.json()['url']
        import_job_id = import_job_url.rstrip('/').rsplit('/', 1)[-1]
        print(f"Successfully created import job file with id: {import_job_id}")

        file_name, file_extension = os.path.splitext(file_name)
        new_name = f'{folder}/processed/{file_name}_{import_job_id}{file_extension}'

        print(f"Moving file {file_path} to processed folder path: {new_name}")
        client_bucket.rename_blob(blob, new_name=new_name)
    else:
        raise Exception(
            f"Failed to create import job, got response status code: {response.status_code}, "
            f"with content: {response.content}"
        )
