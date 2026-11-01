import json
import logging
from unittest.mock import Mock, patch

from requests.exceptions import ConnectionError, HTTPError

from version_check import (
    __version__,
    check_for_update,
    compare_versions,
    get_latest_version,
)


def test_get_latest_version_success(monkeypatch):
    """Test successful fetch of latest version from GitHub."""
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)
    response = Mock()
    response.json.return_value = {"tag_name": "v1.2.3"}

    with patch("version_check.logged_get", return_value=response) as mock_get:
        version = get_latest_version("owner", "repo")

    assert version == "v1.2.3"
    mock_get.assert_called_once_with(
        "https://api.github.com/repos/owner/repo/releases/latest",
        headers={"User-Agent": "explorer-mintchain-to-csv"},
        timeout=5,
    )


def test_get_latest_version_failure():
    """Test graceful handling of a connection error."""
    with patch(
        "version_check.logged_get", side_effect=ConnectionError("Connection error")
    ):
        version = get_latest_version("owner", "repo")

    assert version is None


def test_get_latest_version_http_error_returns_none():
    response = Mock(status_code=404)
    response.raise_for_status.side_effect = HTTPError("Not found")

    with patch("version_check.logged_get", return_value=response):
        version = get_latest_version("owner", "repo")

    assert version is None


def test_get_latest_version_invalid_json_returns_none():
    response = Mock()
    response.json.side_effect = json.JSONDecodeError("Invalid JSON", "{", 0)

    with patch("version_check.logged_get", return_value=response):
        version = get_latest_version("owner", "repo")

    assert version is None


def test_get_latest_version_logs_status_without_authorization_token(
    caplog, monkeypatch
):
    token = "GITHUB_TOKEN_MUST_NOT_APPEAR_IN_LOGS"
    monkeypatch.setenv("GITHUB_TOKEN", token)
    response = Mock(status_code=200)
    response.json.return_value = {"tag_name": "v1.2.3"}

    with patch("fetch_blockchain_data.session.get", return_value=response) as mock_get:
        with caplog.at_level(logging.INFO):
            version = get_latest_version("owner", "repo")

    assert version == "v1.2.3"
    assert "API request method=GET" in caplog.text
    assert "status_code=200" in caplog.text
    assert "duration_ms=" in caplog.text
    assert token not in caplog.text
    assert mock_get.call_args.kwargs["headers"]["Authorization"] == f"token {token}"


def test_compare_versions():
    """Test version comparison."""
    assert compare_versions("1.0.0", "1.2.3") == -1  # current < latest
    assert compare_versions("1.2.3", "1.2.3") == 0  # current == latest
    assert compare_versions("2.0.0", "1.2.3") == 1  # current > latest

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
