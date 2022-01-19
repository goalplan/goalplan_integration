import json

import os
import requests
from google.cloud.storage import Client as StorageClient


class GoalplanStorageClient:

    def __init__(self, dry_run=False):
        self.client = StorageClient()
        self.dry_run = dry_run

    def download_as_bytes(self, bucket_name, file_path):
        if self.dry_run:
            print(f"Will download storage object {file_path} from bucket {bucket_name}.")
            return

        bucket = self.client.bucket(bucket_name)
        blob = bucket.get_blob(file_path)
        file_content = blob.download_as_bytes(raw_download=True)
        print(f"Downloaded storage object {file_path} from bucket {bucket_name}.")
        return file_content

    def rename(self, bucket_name, file_path, new_name):
        if self.dry_run:
            print(f"Will rename file from {file_path} to: {new_name}")
            return

        bucket = self.client.bucket(bucket_name)
        blob = bucket.get_blob(file_path)
        bucket.rename_blob(blob, new_name=new_name)
        print(f"Renamed file from {file_path} to: {new_name}")


class BucketFileImporter:

    def __init__(self, base_url, api_token, file_mappings):
        self.base_url = base_url
        self.api_token = api_token
        self.file_mappings = file_mappings

    @classmethod
    def from_dict(cls, config):
        return cls(
            base_url=config['base_url'],
            api_token=config['api_token'],
            file_mappings=config['file_mappings']
        )

    @classmethod
    def from_config_file(cls, file_path_to_json_config, **config_overrides):
        with open(file_path_to_json_config) as f:
            config = json.load(f)
            config.update(**config_overrides)

        return cls.from_dict(config)

    def _get_matching_definition_id(self, file_folder):
        for folder, definition_id in self.file_mappings.items():
            if folder == file_folder:
                return definition_id

    def _create_import_job(self, definition_id, file_content, content_type, dry_run):
        data_url = self.base_url.rstrip('/') + '/' + definition_id

        if dry_run:
            print(f"Will POST file content to {data_url}.")
            return

        headers = {
            'Authorization': f'Token {self.api_token}',
            'Content-Type': content_type
        }

        response = requests.post(data_url, data=file_content, headers=headers)
        if response.status_code == 202:
            import_job_url = response.json()['url']
            import_job_id = import_job_url.rstrip('/').rsplit('/', 1)[-1]
            print(f"Successfully created import job file with id: {import_job_id}")
            return import_job_id
        else:
            raise Exception(
                f"Failed to create import job, got response status code: {response.status_code}, "
                f"with content: {response.content}"
            )

    def handle(self, bucket, file_path, content_type, dry_run):
        file_folder, file_name = file_path.rsplit('/', maxsplit=1)

        matched_definition_id = self._get_matching_definition_id(file_folder)
        if not matched_definition_id:
            print(f"Ignoring file {file_path}. No match found in configured file_mappings.")
            return
        else:
            print(f"Matched file {file_path}. Using configured definition id {matched_definition_id}.")

        storage_client = GoalplanStorageClient(dry_run=dry_run)
        file_content = storage_client.download_as_bytes(bucket, file_path)

        import_job_id = self._create_import_job(matched_definition_id, file_content, content_type, dry_run)

        file_name, file_extension = os.path.splitext(file_path)
        new_name = f'{file_folder}/processed/{file_name}_{import_job_id}{file_extension}'

        storage_client.rename(bucket, file_path, new_name)

    def handle_event(self, event, context, dry_run):
        bucket = event['bucket']
        file_path = event['name']
        content_type = event['contentType']

        return self.handle(bucket, file_path, content_type, dry_run)
