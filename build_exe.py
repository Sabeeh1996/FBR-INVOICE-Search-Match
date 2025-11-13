"""
Build script to create .exe file using PyInstaller
Run this script to generate the executable
"""

import PyInstaller.__main__
import os
import shutil
from pathlib import Path

def build_exe():
    """Build the executable using PyInstaller"""
    
    # Get the project root
    project_root = Path(__file__).parent
    
    # Define paths
    main_file = str(project_root / "main.py")
    dist_dir = str(project_root / "dist")
    build_dir = str(project_root / "build")
    spec_file = str(project_root / "FBR_Invoice_Checker.spec")
    
    # PyInstaller arguments
    args = [
        main_file,
        '--name=FBR Invoice Checker Bot',
        '--onefile',  # Create single executable file
        '--windowed',  # No console window
        f'--distpath={dist_dir}',
        f'--workpath={build_dir}',
        '--add-data=license_config.json:.',
        '--hidden-import=tkinter',
        '--hidden-import=openpyxl',
        '--collect-submodules=openpyxl',  # Collect all openpyxl submodules
        '--hidden-import=et_xmlfile',  # Required by openpyxl
        '--hidden-import=selenium',
        '--hidden-import=playwright',
        '--hidden-import=undetected_chromedriver',
        '--collect-all=openpyxl',  # Ensure all openpyxl data files are included
    ]
    
    print("🔨 Building FBR Invoice Checker Bot executable...")
    print(f"📂 Project root: {project_root}")
    print(f"📁 Output directory: {dist_dir}")
    print()
    
    try:
        PyInstaller.__main__.run(args)
        print("\n✅ Build successful!")
        print(f"📦 Executable location: {dist_dir}\\FBR Invoice Checker Bot.exe")
        print("\n📋 Next steps:")
        print("1. The executable is in the 'dist' folder")
        print("2. You can move it anywhere or create a shortcut")
        print("3. Run it just like any other Windows application")
        
    except Exception as e:
        print(f"\n❌ Build failed: {str(e)}")
        raise

if __name__ == "__main__":
    build_exe()
