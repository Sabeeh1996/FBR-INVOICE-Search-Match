"""
update_checker.py

This module is responsible for checking GitHub Releases for the latest version
of the application.

Author: Auto-Update System
Date: 2025
"""

import requests
import logging
from typing import Optional, Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UpdateChecker:
    """
    Checks for new versions of the application by querying GitHub Releases API.
    
    This class handles all communication with GitHub to determine if a newer
    version of the application is available.
    """
    
    def __init__(self, repo_owner: str, repo_name: str, github_token: str = None):
        """
        Initialize the UpdateChecker.
        
        Args:
            repo_owner (str): The GitHub username or organization (e.g., "Sabeeh1996")
            repo_name (str): The repository name (e.g., "FBR-INVOICE-Search-Match")
            github_token (str): GitHub Personal Access Token for private repos (optional)
        """
        self.repo_owner = repo_owner
        self.repo_name = repo_name
        self.github_token = github_token
        self.api_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/releases/latest"
        
        # Setup headers with authentication if token provided
        self.headers = {}
        if github_token:
            self.headers['Authorization'] = f'token {github_token}'
            logger.info(f"UpdateChecker initialized for {repo_owner}/{repo_name} (authenticated)")
        else:
            logger.info(f"UpdateChecker initialized for {repo_owner}/{repo_name}")
    
    def get_latest_release(self) -> Optional[Dict[str, Any]]:
        """
        Fetch the latest release information from GitHub.
        
        Returns:
            dict: Release information including version, download URL, etc.
            None: If there was an error or no release found.
            
        Example return value:
            {
                'tag_name': 'v1.2',
                'name': 'Version 1.2',
                'body': 'Release notes...',
                'assets': [{'browser_download_url': '...', 'name': '...'}],
                'published_at': '2025-01-15T10:30:00Z'
            }
        """
        try:
            logger.info("Checking for latest release on GitHub...")
            
            # Set a reasonable timeout to avoid hanging
            response = requests.get(self.api_url, headers=self.headers, timeout=10)
            
            # Check if request was successful
            if response.status_code == 200:
                release_data = response.json()
                logger.info(f"Latest release found: {release_data.get('tag_name', 'Unknown')}")
                return release_data
            elif response.status_code == 404:
                logger.warning("No releases found in the repository (or repository is private without token)")
                return None
            else:
                logger.error(f"GitHub API returned status code: {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Request to GitHub API timed out")
            return None
        except requests.exceptions.ConnectionError:
            logger.error("Unable to connect to GitHub. Please check your internet connection.")
            return None
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching latest release: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return None
    
    def compare_versions(self, current_version: str, latest_version: str) -> bool:
        """
        Compare two version strings to determine if an update is available.
        
        Args:
            current_version (str): Current version (e.g., "1.0" or "v1.0")
            latest_version (str): Latest version from GitHub (e.g., "v1.2")
            
        Returns:
            bool: True if latest_version is newer than current_version, False otherwise
            
        Example:
            compare_versions("1.0", "v1.2") -> True
            compare_versions("1.5", "v1.2") -> False
            compare_versions("1.2", "v1.2") -> False
        """
        try:
            # Remove 'v' prefix if present
            current_clean = current_version.strip().lower().replace('v', '')
            latest_clean = latest_version.strip().lower().replace('v', '')
            
            # Split version numbers by dots
            current_parts = [int(x) for x in current_clean.split('.')]
            latest_parts = [int(x) for x in latest_clean.split('.')]
            
            # Pad shorter version with zeros (e.g., 1.0 becomes 1.0.0)
            max_length = max(len(current_parts), len(latest_parts))
            current_parts += [0] * (max_length - len(current_parts))
            latest_parts += [0] * (max_length - len(latest_parts))
            
            # Compare version parts
            logger.info(f"Comparing versions: {current_clean} vs {latest_clean}")
            
            for curr, latest in zip(current_parts, latest_parts):
                if latest > curr:
                    logger.info(f"New version available: {latest_clean} > {current_clean}")
                    return True
                elif latest < curr:
                    logger.info(f"Current version is newer: {current_clean} > {latest_clean}")
                    return False
            
            # Versions are equal
            logger.info(f"Versions are equal: {current_clean} == {latest_clean}")
            return False
            
        except ValueError as e:
            logger.error(f"Error parsing version numbers: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error comparing versions: {str(e)}")
            return False
    
    def check_for_updates(self, current_version: str) -> Optional[Dict[str, Any]]:
        """
        Check if a new version is available.
        
        This is the main method you'll use in your application.
        It combines fetching the latest release and comparing versions.
        
        Args:
            current_version (str): The current version of your application
            
        Returns:
            dict: Release information if update is available
            None: If no update is available or an error occurred
            
        Example usage:
            checker = UpdateChecker("Sabeeh1996", "FBR-INVOICE-Search-Match")
            update_info = checker.check_for_updates("1.0")
            if update_info:
                print(f"Update available: {update_info['tag_name']}")
        """
        # Get latest release from GitHub
        release_data = self.get_latest_release()
        
        if not release_data:
            logger.info("No release data available")
            return None
        
        # Extract version from release
        latest_version = release_data.get('tag_name', '')
        
        if not latest_version:
            logger.warning("Release has no tag_name")
            return None
        
        # Compare versions
        if self.compare_versions(current_version, latest_version):
            logger.info(f"Update available: {latest_version}")
            return release_data
        else:
            logger.info("Application is up to date")
            return None


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Create an instance of UpdateChecker
    checker = UpdateChecker("Sabeeh1996", "FBR-INVOICE-Search-Match")
    
    # Check for updates
    current_version = "1.1"
    update_info = checker.check_for_updates(current_version)
    
    if update_info:
        print(f"\n✓ Update Available!")
        print(f"  Current Version: {current_version}")
        print(f"  Latest Version: {update_info['tag_name']}")
        print(f"  Release Name: {update_info.get('name', 'N/A')}")
        print(f"  Published: {update_info.get('published_at', 'N/A')}")
        
        # Check if there are any downloadable assets
        assets = update_info.get('assets', [])
        if assets:
            print(f"\n  Available Downloads:")
            for asset in assets:
                print(f"    - {asset['name']} ({asset['size']} bytes)")
        else:
            print("\n  ⚠ No downloadable assets found in this release")
    else:
        print(f"\n✓ Your application is up to date (v{current_version})")
