from pathlib import Path
from unittest import mock
import pytest

from goalplan.google import BucketFileImporter


@pytest.fixture
def mock_context():
    context = mock.MagicMock()
    context.event_id = 'some-id'
    context.event_type = 'test-event'

    return context


@pytest.mark.parametrize('dry_run', [True, False])
def test_handle_file_name_not_matching(dry_run, capsys, mock_context):
    event = {
        'bucket': 'some-bucket',
        'name': 'data-upload/not-matching/test.txt',
        'contentType': 'plain/text'
    }
    config_path = Path(__file__).with_name('config.json')
    client = BucketFileImporter.from_config_file(config_path)

    client.handle_event(event, mock_context, dry_run)
    out, err = capsys.readouterr()

    assert 'Ignoring file data-upload/not-matching/test.txt' in out


@pytest.mark.parametrize('dry_run', [True, False])
def test_file_name_already_processed(dry_run, capsys, mock_context):
    event = {
        'bucket': 'some-bucket',
        'name': 'data-upload/phone-data/processed/test.txt',
        'contentType': 'plain/text'
    }

    config_path = Path(__file__).with_name('config.json')
    client = BucketFileImporter.from_config_file(config_path)

    client.handle_event(event, mock_context, dry_run)
    out, err = capsys.readouterr()

    assert 'Ignoring file data-upload/phone-data/processed/test.txt' in out


@pytest.mark.parametrize('move_to_path', [None, 'goalplan-processed'])
@pytest.mark.parametrize('dry_run', [True, False])
def test_file_name_matching_and_api_call_succeeded(move_to_path, dry_run, capsys, mock_context):
    event = {
        'bucket': 'some-bucket',
        'name': 'data-upload/phone-data/test.txt',
        'contentType': 'plain/text'
    }

    with mock.patch('goalplan.google.StorageClient') as mock_storage_client, \
            mock.patch('goalplan.google.requests') as mock_requests:

        mock_client = mock.MagicMock(status_code=202)
        mock_storage_client.return_value = mock_client

        mock_bucket = mock.MagicMock()
        mock_client.bucket.return_value = mock_bucket

        api_response = mock.MagicMock(status_code=202)
        api_response.json.return_value = {
            'url': 'https://stage-api.goalplan.com/data/importjobs/112846f4-ed97-4a5b-8f63-0a166ca731df/'
        }

        mock_requests.post.return_value = api_response

        client = BucketFileImporter.from_dict({
            "base_url": "https://stage-api.goalplan.com/data/import/",
            "api_token": "test-token",
            "file_mappings": [
                [
                    "data-upload/phone-data/[^/]+.txt",
                    "e23f7a01-d814-452b-8846-5f8d3f70bb09",
                    move_to_path,
                ]
            ],
        })

        client.handle_event(event, mock_context, dry_run)

        if dry_run:
            mock_client.bucket.assert_not_called()
            mock_bucket.get_blob.assert_not_called()
            mock_bucket.rename_blob.assert_not_called()
        else:
            mock_client.bucket.assert_called_with('some-bucket')
            mock_bucket.get_blob.assert_called_with('data-upload/phone-data/test.txt')
            if move_to_path:
                mock_bucket.rename_blob.assert_called()
            else:
                mock_bucket.rename_blob.assert_not_called()

    out, err = capsys.readouterr()
    assert 'Matched file data-upload/phone-data/test.txt' in out

    if dry_run:
        assert "Will download storage object data-upload/phone-data/test.txt from bucket some-bucket." in out
        assert "Will POST file content to " \
               "https://stage-api.goalplan.com/data/import/e23f7a01-d814-452b-8846-5f8d3f70bb09." in out
        if move_to_path is not None:
            assert "Will rename file from data-upload/phone-data/test.txt to:" in out
            assert "goalplan-processed/data-upload/phone-data/test_None.txt" in out
        else:
            assert "Will rename file from data-upload/phone-data/test.txt to:" not in out
    else:
        assert "Downloaded storage object data-upload/phone-data/test.txt from bucket some-bucket." in out
        assert "Successfully created import job file with id: 112846f4-ed97-4a5b-8f63-0a166ca731df" in out
        if move_to_path is not None:
            assert "Renamed file from data-upload/phone-data/test.txt to: " \
                   "goalplan-processed/data-upload/phone-data/" \
                   "test_112846f4-ed97-4a5b-8f63-0a166ca731df.txt" in out
        else:
            assert "Renamed file from data-upload/phone-data/test.txt to: " not in out


@pytest.mark.parametrize('dry_run', [True, False])
def test_file_name_matching_and_api_call_fails(dry_run, capsys, mock_context):
    event = {
        'bucket': 'some-bucket',
        'name': 'data-upload/phone-data/test.txt',
        'contentType': 'plain/text'
    }

    config_path = Path(__file__).with_name('config.json')
    client = BucketFileImporter.from_config_file(config_path)

    with mock.patch('goalplan.google.StorageClient') as mock_storage_client, \
            mock.patch('goalplan.google.requests') as mock_requests:

        mock_client = mock.MagicMock(status_code=202)
        mock_storage_client.return_value = mock_client

        mock_bucket = mock.MagicMock()
        mock_client.bucket.return_value = mock_bucket

        api_response = mock.MagicMock(status_code=400, content='Bad request')
        mock_requests.post.return_value = api_response

        if dry_run:
            client.handle_event(event, mock_context, dry_run)
            mock_client.bucket.assert_not_called()
            mock_bucket.get_blob.assert_not_called()
            mock_bucket.rename_blob.assert_not_called()
        else:
            with pytest.raises(Exception) as exc:
                client.handle_event(event, mock_context, dry_run)

            mock_client.bucket.assert_called_with('some-bucket')
            mock_bucket.get_blob.assert_called_with('data-upload/phone-data/test.txt')
            mock_bucket.rename_blob.assert_not_called()

            assert "Failed to create import job, got response status code: 400, with content: Bad request" == str(
                exc.value)
