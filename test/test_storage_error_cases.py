import pytest
from unittest import mock
import services.storage as storage_module

def test_download_file_not_found(mock_bucket):
    file_name = "non_existent_file.txt"
    mock_bucket.get_blob.return_value = None
    result = storage_module.download_file(file_name)
    mock_bucket.get_blob.assert_called_once_with(file_name)
    assert result is None

