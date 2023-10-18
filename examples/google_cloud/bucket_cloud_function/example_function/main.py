import os

from goalplan.google import BucketFileImporter


def create_import_job(event, context):
    base_url = "https://api.goalplan.com/data/import/"
    api_token = os.environ.get('GOALPLAN_DATA_IMPORT_TOKEN')
    dry_run = True

    if api_token is None and not dry_run:
        raise Exception('GOALPLAN_DATA_IMPORT_TOKEN env variable needs to be set, preferably using secrets.')

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
            "11111111-2222-3333-4444-555555555",
            None
        ]
    ]
    client = BucketFileImporter(base_url, api_token, file_mappings)
    client.handle_event(event, context, dry_run=dry_run)
