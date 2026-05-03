import json
from unittest.mock import patch, MagicMock
from urllib.error import URLError
from version_check import get_latest_version, compare_versions, check_for_update, __version__

def test_get_latest_version_success():
    """Test successful fetch of latest version from GitHub."""
    import io
    mock_data = json.dumps({"tag_name": "v1.2.3"}).encode()
    
    class MockResponse:
        def __enter__(self):
            return self
        def __exit__(self, *args):
            return False
        def read(self):
            return mock_data
    
    with patch("version_check.urlopen", return_value=MockResponse()):
        with patch("version_check.Request"):
            version = get_latest_version("owner", "repo")
            assert version == "v1.2.3"

def test_get_latest_version_failure():
    """Test handling of URL error."""
    with patch("version_check.urlopen", side_effect=URLError("Connection error")):
        version = get_latest_version("owner", "repo")
        assert version is None

def test_compare_versions():
    """Test version comparison."""
    assert compare_versions("1.0.0", "1.2.3") == -1  # current < latest
    assert compare_versions("1.2.3", "1.2.3") == 0   # current == latest
    assert compare_versions("2.0.0", "1.2.3") == 1   # current > latest
    
    # Test with 'v' prefix
    assert compare_versions("v1.0.0", "v1.2.3") == -1
    assert compare_versions("1.0.0", "v1.2.3") == -1

def test_check_for_update_available():
    """Test check_for_update when newer version is available."""
    with patch("version_check.get_latest_version", return_value="v2.0.0"):
        message = check_for_update("owner", "repo")
        assert message is not None
        assert "2.0.0" in message
        assert __version__ in message

def test_check_for_update_not_available():
    """Test check_for_update when no newer version is available."""
    with patch("version_check.get_latest_version", return_value=__version__):
        message = check_for_update("owner", "repo")
        assert message is None

def test_check_for_update_no_latest():
    """Test check_for_update when latest version fetch fails."""
    with patch("version_check.get_latest_version", return_value=None):
        message = check_for_update("owner", "repo")
        assert message is None
