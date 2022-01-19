# Uploading data to Goalplan using Cloud Functions

Requirements:

- Google Cloud Platform account
- Google Cloud Storage Bucket
- If you will deploy the function using the CLI you need to have gcloud cli installed

Data flow: Upload file to bucket -> function uploads to Goalplan -> Moves file to processed directory (done)

## Step by step instructions

- Copy the content of [example_function](example_function) directory to a new directory of your choice
- Deploy the function

```bash
gcloud functions deploy <your-cloud-function-name> \
  --runtime python39 \
  --trigger-resource <bucket name> \
  --trigger-event google.storage.object.finalize
```

- Upload a file in the bucket
- Check the logs, and you should see that the cloud function handles the upload

```bash
gcloud functions logs read
```

- The example code will work without configuration changes, as it will run all code in a "dry run" mode
- When the cloud function is up and running properly, contact your Goalplan integration contact for real configurations.

## Security

We recommend you to store the token using Google Cloud secrets in the cloud function. For more information
that we refer to [Googles documentation about using secrets in Cloud Functions](https://cloud.google.com/functions/docs/configuring/secrets). If you need further
assistance place contact your Goalplan integration contact.

## Reference documentation

Cloud functions: https://cloud.google.com/functions

Storage triggers: https://cloud.google.com/functions/docs/calling/storage
