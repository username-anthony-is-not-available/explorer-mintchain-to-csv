import json
import logging
import os
from typing import Optional, Tuple
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

logger = logging.getLogger(__name__)

# Version of this package
__version__ = "1.0.0"

def get_latest_version(repo_owner: str, repo_name: str) -> Optional[str]:
    """
    Fetches the latest release version from GitHub Releases API.
    
    Args:
        repo_owner: The owner of the repository (e.g., "username")
        repo_name: The name of the repository (e.g., "explorer-mintchain-to-csv")
    
    Returns:
        The latest version string (e.g., "v1.2.3") or None if fetch fails.
    """
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
    try:
        request = Request(url)
        # Add user agent (required by GitHub API)
        request.add_header("User-Agent", "explorer-mintchain-to-csv")
        
        # Add GitHub token if available (for higher rate limits)
        github_token = os.getenv("GITHUB_TOKEN")
        if github_token:
            request.add_header("Authorization", f"token {github_token}")
        
        with urlopen(request, timeout=5) as response:
            data = json.loads(response.read().decode())
            return data.get("tag_name")
    except (URLError, HTTPError, json.JSONDecodeError, KeyError) as e:
        logger.debug(f"Failed to fetch latest version: {e}")
        return None

def compare_versions(current: str, latest: str) -> int:
    """
    Compares two version strings.
    
    Returns:
        -1 if current < latest
         0 if current == latest
         1 if current > latest
    """
    def normalize(v: str) -> Tuple[int, ...]:
        # Remove 'v' prefix if present
        v = v.lstrip('v')
        return tuple(int(x) for x in v.split('.'))
    
    try:
        current_normalized = normalize(current)
        latest_normalized = normalize(latest)
        if current_normalized < latest_normalized:
            return -1
        elif current_normalized > latest_normalized:
            return 1
        return 0
    except (ValueError, AttributeError):
        return 0  # Assume equal if comparison fails

def check_for_update(repo_owner: str, repo_name: str) -> Optional[str]:
    """
    Checks if a newer version is available.
    
    Returns:
        A message string if update is available, None otherwise.
    """
    latest = get_latest_version(repo_owner, repo_name)
    if latest and compare_versions(__version__, latest) < 0:
        return (
            f"Update available: {latest} (current: {__version__}). "
            f"Run 'pip install --upgrade git+https://github.com/{repo_owner}/{repo_name}.git' to update."
        )
    return None

def print_update_notification(repo_owner: str, repo_name: str) -> None:
    """Prints update notification if a newer version is available."""
    message = check_for_update(repo_owner, repo_name)
    if message:
        logger.info(message)
