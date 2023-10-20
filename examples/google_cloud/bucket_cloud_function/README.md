# Uploading data to Goalplan using Cloud Functions

Requirements:

- Google Cloud Platform account
- Google Cloud Storage Bucket
- If you will deploy the function using the CLI you need to have gcloud cli installed

Data flow: Upload file to bucket -> function uploads to Goalplan -> Moves file to processed directory (done)

## Step by step instructions

- Download and unzip [bucket_cloud_function_example.zip](bucket_cloud_function_example.zip) to a folder of your choice
- Update the configuration in main.py to match the pattern of the files that should be uploaded to Goalplan
- Deploy the function

```bash
gcloud functions deploy <your-function-name> \
  --trigger-resource <google-cloud-bucket-name>  \
  --trigger-event google.storage.object.finalize \
  --set-secrets GOALPLAN_DATA_IMPORT_TOKEN=<secret-name>:<secret-version> \
  --entry-point create_import_job \
  --runtime python311
```

- Upload a file in the bucket
- Check the logs, and you should see that the cloud function handles the upload

```bash
gcloud functions logs read
```

- Please note that there is a potential bug in gcloud functions deploy that causes re-deploy to fail. A workaround
  for this problem is that you delete the function and then deploy the function again.

```bash
gcloud functions delete <your-function-name>
```


## Security

We recommend you to store the token using Google Cloud secrets in the cloud function. For more information
that we refer to [Googles documentation about using secrets in Cloud Functions](https://cloud.google.com/functions/docs/configuring/secrets). If you need further
assistance place contact your Goalplan integration contact.

### roles/secretmanager.secretAccessor

When you added the secret as per Googles documentation, you need to assure that the service account that is running the
cloud function has the **roles/secretmanager.secretAccessor** permission. To find out what service account is running
the cloud function:

```bash
gcloud functions describe <your-function-name>
```

## Reference documentation

Install gcloud cli: https://cloud.google.com/sdk/docs/install-sdk

Cloud functions: https://cloud.google.com/functions

Storage triggers: https://cloud.google.com/functions/docs/calling/storage
