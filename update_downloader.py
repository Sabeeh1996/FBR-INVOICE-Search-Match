"""
update_downloader.py

This module handles downloading update files from GitHub Releases.
It includes progress tracking, error handling, and safe file operations.

Author: Auto-Update System
Date: 2025
"""

import os
import requests
import logging
from typing import Optional, Callable

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class UpdateDownloader:
    """
    Downloads update files from GitHub Releases with proper error handling.
    
    This class manages the download process, including progress tracking,
    retry logic, and safe file storage.
    """
    
    def __init__(self, download_dir: Optional[str] = None):
        """
        Initialize the UpdateDownloader.
        
        Args:
            download_dir (str, optional): Directory to save downloads.
                                         Defaults to current directory.
        """
        self.download_dir = download_dir or os.getcwd()
        
        # Create download directory if it doesn't exist
        if not os.path.exists(self.download_dir):
            os.makedirs(self.download_dir)
            logger.info(f"Created download directory: {self.download_dir}")
        
        logger.info(f"UpdateDownloader initialized. Download path: {self.download_dir}")
    
    def download_file(
        self,
        url: str,
        filename: str = "update.zip",
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Optional[str]:
        """
        Download a file from a URL with progress tracking.
        
        Args:
            url (str): The download URL
            filename (str): Name to save the file as (default: "update.zip")
            progress_callback (callable, optional): Function called with (downloaded_bytes, total_bytes)
                                                   to report progress
        
        Returns:
            str: Full path to the downloaded file
            None: If download failed
            
        Example:
            downloader = UpdateDownloader()
            
            def show_progress(downloaded, total):
                percent = (downloaded / total) * 100
                print(f"Progress: {percent:.1f}%")
            
            file_path = downloader.download_file(
                "https://github.com/.../update.zip",
                progress_callback=show_progress
            )
        """
        file_path = os.path.join(self.download_dir, filename)
        
        try:
            logger.info(f"Starting download from: {url}")
            logger.info(f"Saving to: {file_path}")
            
            # Start the download with streaming to handle large files
            response = requests.get(url, stream=True, timeout=30)
            
            # Check if request was successful
            if response.status_code != 200:
                logger.error(f"Download failed with status code: {response.status_code}")
                return None
            
            # Get total file size from headers
            total_size = int(response.headers.get('content-length', 0))
            
            if total_size == 0:
                logger.warning("Unable to determine file size")
            else:
                logger.info(f"File size: {self._format_size(total_size)}")
            
            # Download the file in chunks
            downloaded_size = 0
            chunk_size = 8192  # 8 KB chunks
            
            with open(file_path, 'wb') as file:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    if chunk:  # Filter out keep-alive chunks
                        file.write(chunk)
                        downloaded_size += len(chunk)
                        
                        # Call progress callback if provided
                        if progress_callback and total_size > 0:
                            try:
                                progress_callback(downloaded_size, total_size)
                            except Exception as e:
                                logger.warning(f"Progress callback error: {str(e)}")
            
            logger.info(f"Download completed: {self._format_size(downloaded_size)}")
            
            # Verify file was created and has content
            if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
                logger.info(f"File verified: {file_path}")
                return file_path
            else:
                logger.error("Downloaded file is empty or doesn't exist")
                return None
                
        except requests.exceptions.Timeout:
            logger.error("Download timed out")
            self._cleanup_file(file_path)
            return None
            
        except requests.exceptions.ConnectionError:
            logger.error("Connection error during download. Check your internet connection.")
            self._cleanup_file(file_path)
            return None
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading file: {str(e)}")
            self._cleanup_file(file_path)
            return None
            
        except IOError as e:
            logger.error(f"Error writing file: {str(e)}")
            self._cleanup_file(file_path)
            return None
            
        except Exception as e:
            logger.error(f"Unexpected error during download: {str(e)}")
            self._cleanup_file(file_path)
            return None
    
    def download_from_release(self, release_data: dict) -> Optional[str]:
        """
        Download the first asset from a GitHub release.
        
        This is a convenience method that extracts the download URL
        from GitHub release data and downloads it.
        
        Args:
            release_data (dict): Release information from GitHub API
            
        Returns:
            str: Path to downloaded file
            None: If download failed or no assets found
            
        Example:
            downloader = UpdateDownloader()
            # Assume release_data came from UpdateChecker
            file_path = downloader.download_from_release(release_data)
            if file_path:
                print(f"Update downloaded: {file_path}")
        """
        try:
            # Get assets from release
            assets = release_data.get('assets', [])
            
            if not assets:
                logger.error("No assets found in release")
                return None
            
            # Get the first asset (usually the installer or ZIP file)
            first_asset = assets[0]
            download_url = first_asset.get('browser_download_url')
            asset_name = first_asset.get('name', 'update.zip')

            if not download_url:
                logger.error("No download URL found in asset")
                return None

            logger.info(f"Downloading asset: {asset_name}")

            # Download using the asset's actual filename
            return self.download_file(download_url, filename=asset_name)
            
        except KeyError as e:
            logger.error(f"Missing required field in release data: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error processing release data: {str(e)}")
            return None
    
    def _cleanup_file(self, file_path: str):
        """
        Delete a partially downloaded file.
        
        Args:
            file_path (str): Path to file to delete
        """
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"Cleaned up incomplete download: {file_path}")
        except Exception as e:
            logger.warning(f"Could not clean up file {file_path}: {str(e)}")
    
    @staticmethod
    def _format_size(bytes_size: int) -> str:
        """
        Format bytes into human-readable size.
        
        Args:
            bytes_size (int): Size in bytes
            
        Returns:
            str: Formatted size string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024.0:
                return f"{bytes_size:.2f} {unit}"
            bytes_size /= 1024.0
        return f"{bytes_size:.2f} TB"


# Example usage (for testing purposes)
if __name__ == "__main__":
    # Simple progress display function
    def show_progress(downloaded, total):
        """Display download progress as percentage."""
        if total > 0:
            percent = (downloaded / total) * 100
            print(f"\rProgress: {percent:.1f}% ({downloaded}/{total} bytes)", end='')
    
    # Example 1: Download from direct URL
    print("Example 1: Direct URL download")
    print("-" * 50)
    downloader = UpdateDownloader()
    
    # Note: Replace with actual URL for testing
    test_url = "https://github.com/Sabeeh1996/FBR-INVOICE-Search-Match/releases/download/v1.1/update.zip"
    
    print(f"Attempting to download from: {test_url}")
    result = downloader.download_file(test_url, progress_callback=show_progress)
    
    if result:
        print(f"\n✓ Download successful: {result}")
    else:
        print("\n✗ Download failed (this is expected if URL doesn't exist)")
    
    print("\n" + "-" * 50)
    print("\nExample 2: Download from release data")
    print("-" * 50)
    
    # Example release data structure
    example_release = {
        'tag_name': 'v1.2',
        'assets': [
            {
                'name': 'FBR-Update-v1.2.zip',
                'browser_download_url': 'https://github.com/.../example.zip',
                'size': 1024000
            }
        ]
    }
    
    print("Release data:", example_release)
    result = downloader.download_from_release(example_release)
    
    if result:
        print(f"\n✓ Download successful: {result}")
    else:
        print("\n✗ Download failed (this is expected for example data)")
