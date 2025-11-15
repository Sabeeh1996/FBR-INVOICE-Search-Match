"""
Complete EXE Build Script for FBR Invoice Checker
Builds a standalone executable with all dependencies
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

print("=" * 70)
print("FBR Invoice Checker - Complete EXE Build")
print("=" * 70)
print()

# Get project directory
PROJECT_DIR = Path(__file__).parent
os.chdir(PROJECT_DIR)

print(f"Project Directory: {PROJECT_DIR}")
print(f"Python: {sys.executable}")
print(f"Python Version: {sys.version}")
print()

# Step 1: Clean previous builds
print("[1/5] Cleaning previous builds...")
for dir_name in ['build', 'dist', '__pycache__']:
    dir_path = PROJECT_DIR / dir_name
    if dir_path.exists():
        shutil.rmtree(dir_path, ignore_errors=True)
        print(f"  ✓ Removed {dir_name}/")

for spec_file in PROJECT_DIR.glob('*.spec'):
    spec_file.unlink()
    print(f"  ✓ Removed {spec_file.name}")

print()

# Step 2: Install/verify dependencies
print("[2/5] Verifying dependencies...")
required_packages = [
    'pyinstaller',
    'requests',
    'selenium',
    'openpyxl',
    'pillow',
    'tkinter'
]

for package in required_packages:
    if package == 'tkinter':
        continue  # Built-in
    try:
        __import__(package.replace('-', '_'))
        print(f"  ✓ {package}")
    except ImportError:
        print(f"  ✗ {package} - Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', package], 
                      capture_output=True)

print()

# Step 3: Create PyInstaller command
print("[3/5] Building executable...")
print("  This will take 5-10 minutes, please wait...")
print()

# Build command
cmd = [
    'pyinstaller',
    '--name=InvoiceChecker',
    '--onefile',
    '--windowed',
    '--noconfirm',
    '--clean',
    
    # Add data files
    # Hidden imports (config files now bundled via spec file)
    '--hidden-import=tkinter',
    '--hidden-import=tkinter.ttk',
    '--hidden-import=tkinter.messagebox',
    '--hidden-import=tkinter.filedialog',
    '--hidden-import=openpyxl',
    '--hidden-import=openpyxl.cell',
    '--hidden-import=openpyxl.styles',
    '--hidden-import=selenium',
    '--hidden-import=selenium.webdriver',
    '--hidden-import=requests',
    '--hidden-import=PIL',
    '--hidden-import=PIL.Image',
    '--hidden-import=PIL.ImageTk',
    
    # Collect all for openpyxl
    '--collect-all=openpyxl',
    
    # Exclude unnecessary packages to reduce size
    '--exclude-module=matplotlib',
    '--exclude-module=pandas',
    '--exclude-module=numpy',
    '--exclude-module=scipy',
    '--exclude-module=pytest',
    
    # Main file
    'main.py'
]

# Run build
try:
    result = subprocess.run(cmd, capture_output=False, text=True)
    if result.returncode != 0:
        print("\n✗ Build failed!")
        sys.exit(1)
except KeyboardInterrupt:
    print("\n\n✗ Build cancelled by user")
    sys.exit(1)
except Exception as e:
    print(f"\n✗ Build error: {e}")
    sys.exit(1)

print()

# Step 4: Verify build
print("[4/5] Verifying build...")
exe_path = PROJECT_DIR / 'dist' / 'InvoiceChecker.exe'

if exe_path.exists():
    size_mb = exe_path.stat().st_size / (1024 * 1024)
    print(f"  ✓ EXE created: {exe_path}")
    print(f"  ✓ Size: {size_mb:.1f} MB")
else:
    print("  ✗ EXE file not found!")
    sys.exit(1)

print()

# Step 5: Create distribution package
print("[5/5] Creating distribution package...")
dist_dir = PROJECT_DIR / 'dist'

# Copy required files to dist
files_to_copy = [
    'license_config.json',
    'version.txt'
]

for file_name in files_to_copy:
    src = PROJECT_DIR / file_name
    if src.exists():
        dst = dist_dir / file_name
        shutil.copy2(src, dst)
        print(f"  ✓ Copied {file_name}")

print()
print("=" * 70)
print("BUILD SUCCESSFUL!")
print("=" * 70)
print()
print(f"Executable: {exe_path}")
print(f"Size: {size_mb:.1f} MB")
print()
print("Files in dist folder:")
for item in sorted(dist_dir.iterdir()):
    if item.is_file():
        size = item.stat().st_size / 1024
        unit = "KB" if size < 1024 else "MB"
        size_val = size if size < 1024 else size / 1024
        print(f"  • {item.name} ({size_val:.1f} {unit})")
print()
print("✓ Ready to distribute!")
print()
print("To test: cd dist && .\\InvoiceChecker.exe")
print()
