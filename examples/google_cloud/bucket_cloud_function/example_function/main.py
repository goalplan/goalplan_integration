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
    """
    file_mappings is a list of file patterns that will trigger upload to Goalplan. Only first match will be processed, 
    so order is important. Each mapping have three entries:
    
    1. Regular expressing matching the path of the uploaded file to the bucket
    2. The Goalplan data identifier that the file will be mapped to
    3. Path where the uploaded file will be moved to. If set to null/None file will remain.
    """
    file_mappings = [
        [
            "drop-folder/match[^/]+.csv",
            "d02e4c2d-55ef-4074-8029-ca1866246a14",
            None
        ]
    ]
    client = BucketFileImporter(base_url, api_token, file_mappings)

    # or read from dictionary
    # config = {
    #     "base_url": "https://api.example.com/data/import/",
    #     "api_token": "******",
    #     "file_mappings": [
    #         [
    #             "drop-folder/match[^/]+.csv",
    #             "d02e4c2d-55ef-4074-8029-ca1866246a14",
    #             None
    #         ]
    #     ]
    # }
    # client = BucketFileImporter.from_dict(config)

    # or read from json config file
    # client = BucketFileImporter.from_config_file('config.json')

    # Use dry_run=False once you want to go live
    client.handle_event(event, context, dry_run=True)
