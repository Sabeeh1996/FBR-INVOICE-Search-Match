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
        '--name=FBR Invoice Checker',  # Generic name to avoid firewall blocking
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
        '--exclude-module=PyQt5',  # Exclude PyQt5 to avoid conflicts with PyQt6
        '--exclude-module=PySide2',  # Exclude PySide2
        '--exclude-module=PySide6',  # Exclude PySide6
        '--exclude-module=matplotlib',  # Exclude matplotlib if not needed
        '--exclude-module=torch',  # Exclude torch - not needed
        '--exclude-module=scipy',  # Exclude scipy - not needed
        '--exclude-module=IPython',  # Exclude IPython - not needed
        '--exclude-module=sphinx',  # Exclude sphinx - not needed
        '--exclude-module=pytest',  # Exclude pytest - not needed
        '--exclude-module=pandas',  # Exclude pandas - not needed
        '--exclude-module=numpy',  # Exclude numpy - not needed
    ]
    
    print("🔨 Building InvoiceChecker executable...")
    print(f"📂 Project root: {project_root}")
    print(f"📁 Output directory: {dist_dir}")
    print()
    
    try:
        PyInstaller.__main__.run(args)
        
        # Clean up: Remove license_config.json from dist if it was copied there
        dist_license = os.path.join(dist_dir, "license_config.json")
        if os.path.exists(dist_license):
            os.remove(dist_license)
            print(f"🗑️  Removed standalone license file from dist (bundled in exe)")
        
        print("\n✅ Build successful!")
        print(f"📦 Executable location: {dist_dir}\\InvoiceChecker.exe")
        print("\n📋 Next steps:")
        print("1. The executable is in the 'dist' folder")
        print("2. You can move it anywhere or create a shortcut")
        print("3. Run it just like any other Windows application")
        print("\n🔒 Security:")
        print("- License config is bundled INSIDE the .exe (not modifiable by users)")
        print("- Users cannot change the expiry date")
        print("- Generic name to prevent firewall blocking")
        
    except Exception as e:
        print(f"\n❌ Build failed: {str(e)}")
        raise

if __name__ == "__main__":
    build_exe()
