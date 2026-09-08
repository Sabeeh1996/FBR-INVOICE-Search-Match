"""
release.py

One-shot release pipeline:
  1. Read the version to ship from version.txt
  2. Rebuild InvoiceChecker.exe from the spec
  3. Compile the Inno Setup installer for that version
  4. Optionally publish a GitHub release with the installer attached
     (requires `gh auth login` to have been run already)

Usage:
    python release.py            # build only
    python release.py --publish  # build + create/update GitHub release
"""

import subprocess
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
ISCC = Path.home() / "AppData" / "Local" / "Programs" / "Inno Setup 6" / "ISCC.exe"


def read_version() -> str:
    version_file = PROJECT_ROOT / "version.txt"
    return version_file.read_text(encoding="utf-8").strip()


def run(cmd, **kwargs):
    print(f"$ {' '.join(str(c) for c in cmd)}")
    result = subprocess.run(cmd, cwd=PROJECT_ROOT, **kwargs)
    if result.returncode != 0:
        sys.exit(f"Command failed: {' '.join(str(c) for c in cmd)}")


def main():
    publish = "--publish" in sys.argv
    version = read_version()
    print(f"Releasing version {version}")

    python_exe = PROJECT_ROOT / ".venv" / "Scripts" / "python.exe"
    run([str(python_exe), "-m", "PyInstaller", "InvoiceChecker.spec", "--noconfirm"])

    if not ISCC.exists():
        sys.exit(f"Inno Setup compiler not found at {ISCC}")
    run([str(ISCC), f"/DMyAppVersion={version}", "installer.iss"])

    installer_path = PROJECT_ROOT / "installer_output" / f"FBR_Invoice_Checker_Setup_v{version}.exe"
    if not installer_path.exists():
        sys.exit(f"Expected installer not found: {installer_path}")
    print(f"Installer ready: {installer_path}")

    if publish:
        tag = f"v{version}"
        run([
            "gh", "release", "create", tag,
            str(installer_path),
            "--title", f"Version {version}",
            "--notes", f"Release {version}",
        ])
        print(f"Published GitHub release {tag} with {installer_path.name} attached.")
    else:
        print("Build complete. Run with --publish to also create a GitHub release.")


if __name__ == "__main__":
    main()
