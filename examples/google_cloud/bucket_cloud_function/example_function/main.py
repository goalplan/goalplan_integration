from goalplan.google import BucketFileImporter


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
    base_url = "https://api.example.com/data/import/"
    api_token = "******"
    file_mappings = {
        "data-upload/phone-data": "a23f7a01-d814-452b-8846-5f8d3f70bb09"
    }

    client = BucketFileImporter(base_url, api_token, file_mappings)

    # or read from dictionary
    # config = {
    #     "base_url": "https://api.example.com/data/import/",
    #     "api_token": "******",
    #     "file_mappings": {
    #         "data-upload/phone-data": "a23f7a01-d814-452b-8846-5f8d3f70bb09"
    #     }
    # }
    # BucketFileImporter.from_dict(config)

    # or read from json config file
    # client = BucketFileImporter.from_config_file('config.json')

    # Use dry_run=False once you want to go live
    client.handle_event(event, context, dry_run=True)

