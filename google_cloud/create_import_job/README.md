# Uploading data to Goalplan using Cloud Functions

## Reference documentation

Cloud functions: https://cloud.google.com/functions

Storage triggers: https://cloud.google.com/functions/docs/calling/storage

## Sample commands

Deploying the function

```bash
gcloud functions deploy create_import_job \\
  --runtime python39 \\
  --trigger-resource <bucket name> \\
  --trigger-event google.storage.object.finalize \\
  --env-vars-file=env.yaml
```

Reading the logs

```bash
gcloud functions logs read
```

