from unittest import mock
import pytest

from google_cloud.create_import_job import main


@pytest.fixture
def mock_context():
    context = mock.MagicMock()
    context.event_id = 'some-id'
    context.event_type = 'test-event'

    return context


def test_file_name_not_matching(capsys, mock_context):
    event = {
        'bucket': 'some-bucket',
        'name': 'data-upload/not-matching/test.txt',
        'contentType': 'plain/text'
    }

    main.create_import_job(event, mock_context)
    out, err = capsys.readouterr()

    assert 'Ignoring file data-upload/not-matching/test.txt' in out


def test_file_name_already_processed(capsys, mock_context):
    event = {
        'bucket': 'some-bucket',
        'name': 'data-upload/phone-data/processed/test.txt',
        'contentType': 'plain/text'
    }

    main.create_import_job(event, mock_context)
    out, err = capsys.readouterr()

    assert 'Ignoring file data-upload/phone-data/processed/test.txt' in out


def test_file_name_matching_and_api_call_succeeded(capsys, mock_context):
    event = {
        'bucket': 'some-bucket',
        'name': 'data-upload/phone-data/test.txt',
        'contentType': 'plain/text'
    }

    with mock.patch('google_cloud.create_import_job.main.StorageClient') as mock_storage_client, \
            mock.patch('google_cloud.create_import_job.main.requests') as mock_requests:

        mock_client = mock.MagicMock(status_code=202)
        mock_storage_client.return_value = mock_client

        mock_bucket = mock.MagicMock()
        mock_client.bucket.return_value = mock_bucket

        api_response = mock.MagicMock(status_code=202)
        api_response.json.return_value = {
            'url': 'https://stage-api.goalplan.com/data/importjobs/112846f4-ed97-4a5b-8f63-0a166ca731df/'
        }

        mock_requests.post.return_value = api_response

        main.create_import_job(event, mock_context)

        mock_client.bucket.assert_called_with('some-bucket')
        mock_bucket.get_blob.assert_called_with('data-upload/phone-data/test.txt')
        mock_bucket.rename_blob.assert_called()

    out, err = capsys.readouterr()
    assert 'Matched file data-upload/phone-data/test.txt' in out
    assert 'Successfully created import job file with id: 112846f4-ed97-4a5b-8f63-0a166ca731df' in out
    assert 'Moving file data-upload/phone-data/test.txt to processed folder path: ' \
           'data-upload/phone-data/processed/test_112846f4-ed97-4a5b-8f63-0a166ca731df.txt' in out


def test_file_name_matching_and_api_call_fails(capsys, mock_context):
    event = {
        'bucket': 'some-bucket',
        'name': 'data-upload/phone-data/test.txt',
        'contentType': 'plain/text'
    }

    with mock.patch('google_cloud.create_import_job.main.StorageClient') as mock_storage_client, \
            mock.patch('google_cloud.create_import_job.main.requests') as mock_requests:

        mock_client = mock.MagicMock(status_code=202)
        mock_storage_client.return_value = mock_client

        mock_bucket = mock.MagicMock()
        mock_client.bucket.return_value = mock_bucket

        api_response = mock.MagicMock(status_code=400, content='Bad request')
        mock_requests.post.return_value = api_response

        with pytest.raises(Exception) as exc:
            main.create_import_job(event, mock_context)

        mock_client.bucket.assert_called_with('some-bucket')
        mock_bucket.get_blob.assert_called_with('data-upload/phone-data/test.txt')
        mock_bucket.rename_blob.assert_not_called()

    out, err = capsys.readouterr()
    assert 'Matched file data-upload/phone-data/test.txt' in out
    assert 'Failed to create import job, got response status code: 400, with content: Bad request' == str(exc.value)



