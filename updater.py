"""
updater.py

Wires update_checker / update_downloader together to detect a newer
GitHub release and hand off to the installer it publishes.

The app ships as a single onefile exe built with Inno Setup, so "applying"
an update means: download the new Setup.exe asset from the release,
launch it silently, then exit this process so the installer can
overwrite the running exe and relaunch the app.
"""

import os
import sys
import json
import logging
import tempfile
import subprocess

from update_checker import UpdateChecker
from update_downloader import UpdateDownloader
from version_manager import read_version, get_resource_path

logger = logging.getLogger(__name__)

REPO_OWNER = "Sabeeh1996"
REPO_NAME = "FBR-INVOICE-Search-Match"


def _load_github_token():
    """
    Load the GitHub token bundled into the exe (github_update_config.json),
    if present. Returns None for a public repo / no config.
    """
    try:
        config_path = get_resource_path("github_update_config.json")
        if not os.path.exists(config_path):
            return None
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f).get("github_token")
    except Exception as e:
        logger.warning(f"Could not load GitHub update token: {e}")
        return None


def _pick_installer_asset(release_data):
    """
    Pick the installer asset from a release's assets list.
    Prefers a Windows Setup .exe; falls back to any .exe asset.
    """
    assets = release_data.get("assets", [])
    exe_assets = [a for a in assets if a.get("name", "").lower().endswith(".exe")]
    if not exe_assets:
        return None

    for asset in exe_assets:
        if "setup" in asset.get("name", "").lower():
            return asset
    return exe_assets[0]


class Updater:
    """High-level update workflow used by the GUI/main entry point."""

    def __init__(self):
        self.token = _load_github_token()
        self.checker = UpdateChecker(REPO_OWNER, REPO_NAME, github_token=self.token)

    def get_current_version(self) -> str:
        version, _ = read_version()
        return version

    def check_for_updates(self):
        """
        Returns (available: bool, release_data: dict or None).
        """
        current_version = self.get_current_version()
        release_data = self.checker.check_for_updates(current_version)
        return (release_data is not None), release_data

    def check_and_apply_updates(self, progress_callback=None, force_update=False):
        """
        Check for an update and, if one is available with a usable installer
        asset, download it and launch it.

        Returns (success: bool, message: str). On success, message contains
        "restart" when the installer has been launched and this process
        should exit immediately so the installer can replace it.
        """
        available, release_data = self.check_for_updates()

        if not available:
            return True, "Application is up to date"

        latest_version = release_data.get("tag_name", "unknown")
        asset = _pick_installer_asset(release_data)

        if not asset:
            msg = f"Update {latest_version} is available, but no installer asset was found"
            logger.warning(msg)
            return (not force_update), msg

        download_url = asset.get("browser_download_url")
        asset_name = asset.get("name", "Setup.exe")

        downloader = UpdateDownloader(download_dir=tempfile.gettempdir())
        installer_path = downloader.download_file(
            download_url, filename=asset_name, progress_callback=progress_callback
        )

        if not installer_path:
            msg = f"Failed to download update {latest_version}"
            logger.error(msg)
            return (not force_update), msg

        try:
            subprocess.Popen(
                [installer_path, "/VERYSILENT", "/SUPPRESSMSGBOXES", "/NORESTART"],
                close_fds=True,
                creationflags=getattr(subprocess, "DETACHED_PROCESS", 0),
            )
        except Exception as e:
            msg = f"Failed to launch installer: {e}"
            logger.error(msg)
            return False, msg

        logger.info(f"Installer launched for {latest_version} - restart required")
        return True, f"Update {latest_version} downloaded - restart required"


def check_and_apply_updates(progress_callback=None, force_update=False):
    """Module-level convenience wrapper used by integration examples."""
    return Updater().check_and_apply_updates(
        progress_callback=progress_callback, force_update=force_update
    )
