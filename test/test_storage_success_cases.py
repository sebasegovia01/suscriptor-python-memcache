import pytest
from unittest import mock
import services.storage as storage_module

@pytest.mark.asyncio
async def test_upload_file(mock_bucket):
    file_content = b"test content"
    file_name = "test_file.txt"
    content_type = "text/plain"
    mock_blob = mock_bucket.blob.return_value
    mock_blob.upload_from_string.return_value = None
    result = await storage_module.upload_file(file_content, file_name, content_type)
    mock_bucket.blob.assert_called_once_with(file_name)
    mock_blob.upload_from_string.assert_called_once_with(file_content, content_type)
    assert result == file_name

def test_download_file(mock_bucket):
    file_name = "test_file.txt"
    file_content = b"test content"
    mock_blob = mock_bucket.get_blob.return_value
    mock_blob.download_as_bytes.return_value = file_content
    result = storage_module.download_file(file_name)
    mock_bucket.get_blob.assert_called_once_with(file_name)
    mock_blob.download_as_bytes.assert_called_once()
    assert result == file_content

def test_list_files(mock_bucket):
    mock_blob1 = mock.Mock()
    mock_blob1.name = "file1.txt"
    mock_blob2 = mock.Mock()
    mock_blob2.name = "file2.txt"
    mock_bucket.list_blobs.return_value = [mock_blob1, mock_blob2]
    result = storage_module.list_files()
    mock_bucket.list_blobs.assert_called_once()
    assert result == ["file1.txt", "file2.txt"]

