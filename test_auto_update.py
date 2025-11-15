"""
test_auto_update.py

Test script to verify the auto-update system is working correctly.
Run this to test each component before deploying.
"""

import os
import sys

def print_header(title):
    """Print a nice header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_test(test_name, passed):
    """Print test result."""
    status = "✓ PASS" if passed else "✗ FAIL"
    print(f"  [{status}] {test_name}")

def test_imports():
    """Test that all modules can be imported."""
    print_header("TEST 1: Module Imports")
    
    tests = []
    
    try:
        from update_checker import UpdateChecker
        tests.append(("update_checker.py", True))
    except Exception as e:
        tests.append(("update_checker.py", False))
        print(f"  Error: {e}")
    
    try:
        from update_downloader import UpdateDownloader
        tests.append(("update_downloader.py", True))
    except Exception as e:
        tests.append(("update_downloader.py", False))
        print(f"  Error: {e}")
    
    try:
        from update_installer import UpdateInstaller
        tests.append(("update_installer.py", True))
    except Exception as e:
        tests.append(("update_installer.py", False))
        print(f"  Error: {e}")
    
    try:
        from updater import Updater, check_and_apply_updates
        tests.append(("updater.py", True))
    except Exception as e:
        tests.append(("updater.py", False))
        print(f"  Error: {e}")
    
    for test_name, result in tests:
        print_test(test_name, result)
    
    return all(result for _, result in tests)

def test_version_file():
    """Test version.txt exists and is readable."""
    print_header("TEST 2: Version File")
    
    version_file = "version.txt"
    
    if not os.path.exists(version_file):
        print_test("version.txt exists", False)
        print(f"  Error: {version_file} not found")
        return False
    
    print_test("version.txt exists", True)
    
    try:
        with open(version_file, 'r') as f:
            version = f.read().strip()
        
        print_test("version.txt is readable", True)
        print(f"  Current version: {version}")
        
        if not version:
            print_test("version.txt has content", False)
            return False
        
        print_test("version.txt has content", True)
        return True
        
    except Exception as e:
        print_test("version.txt is readable", False)
        print(f"  Error: {e}")
        return False

def test_github_connection():
    """Test connection to GitHub API."""
    print_header("TEST 3: GitHub Connection")
    
    try:
        from update_checker import UpdateChecker
        
        checker = UpdateChecker("Sabeeh1996", "FBR-INVOICE-Search-Match")
        print("  Connecting to GitHub API...")
        
        release_data = checker.get_latest_release()
        
        if release_data:
            print_test("GitHub API accessible", True)
            print(f"  Latest release: {release_data.get('tag_name', 'Unknown')}")
            print(f"  Published: {release_data.get('published_at', 'Unknown')}")
            
            assets = release_data.get('assets', [])
            print(f"  Assets: {len(assets)} file(s)")
            
            if assets:
                print_test("Release has assets", True)
                for asset in assets:
                    print(f"    - {asset['name']} ({asset['size']} bytes)")
            else:
                print_test("Release has assets", False)
                print("  Warning: No downloadable assets in release")
            
            return True
        else:
            print_test("GitHub API accessible", False)
            print("  Warning: No releases found or API unavailable")
            return False
            
    except Exception as e:
        print_test("GitHub connection", False)
        print(f"  Error: {e}")
        return False

def test_version_comparison():
    """Test version comparison logic."""
    print_header("TEST 4: Version Comparison")
    
    try:
        from update_checker import UpdateChecker
        
        checker = UpdateChecker("Sabeeh1996", "FBR-INVOICE-Search-Match")
        
        tests = [
            ("1.0", "v1.1", True, "1.0 < 1.1"),
            ("1.1", "v1.0", False, "1.1 > 1.0"),
            ("1.0", "v1.0", False, "1.0 = 1.0"),
            ("1.0.0", "v1.0.1", True, "1.0.0 < 1.0.1"),
            ("2.0", "v1.9", False, "2.0 > 1.9"),
        ]
        
        all_passed = True
        
        for current, latest, expected, description in tests:
            result = checker.compare_versions(current, latest)
            passed = result == expected
            all_passed = all_passed and passed
            print_test(description, passed)
            if not passed:
                print(f"    Expected: {expected}, Got: {result}")
        
        return all_passed
        
    except Exception as e:
        print_test("Version comparison", False)
        print(f"  Error: {e}")
        return False

def test_update_check():
    """Test full update check."""
    print_header("TEST 5: Update Check")
    
    try:
        from updater import Updater
        
        updater = Updater()
        current_version = updater.get_current_version()
        
        print(f"  Current version: {current_version}")
        print("  Checking for updates...")
        
        available, release_data = updater.check_for_updates()
        
        if available:
            print_test("Update check completed", True)
            print(f"  ⚠ Update available: {release_data['tag_name']}")
            print(f"  Current: v{current_version}")
            print(f"  Latest: {release_data['tag_name']}")
            return True
        else:
            print_test("Update check completed", True)
            print(f"  ✓ Application is up to date (v{current_version})")
            return True
            
    except Exception as e:
        print_test("Update check", False)
        print(f"  Error: {e}")
        return False

def test_backup_creation():
    """Test backup functionality."""
    print_header("TEST 6: Backup System")
    
    try:
        from update_installer import UpdateInstaller
        
        installer = UpdateInstaller()
        
        print("  Creating test backup...")
        success = installer.create_backup()
        
        print_test("Backup creation", success)
        
        if success:
            backup_dir = installer.backup_dir
            if os.path.exists(backup_dir):
                print(f"  Backup location: {backup_dir}")
                files = os.listdir(backup_dir)
                print(f"  Files backed up: {len(files)}")
                
                # Clean up test backup
                print("  Cleaning up test backup...")
                installer.cleanup_backup()
                
                return True
        
        return success
        
    except Exception as e:
        print_test("Backup system", False)
        print(f"  Error: {e}")
        return False

def test_dependencies():
    """Test required dependencies."""
    print_header("TEST 7: Dependencies")
    
    dependencies = [
        ("requests", "For downloading updates"),
        ("zipfile", "For extracting updates (built-in)"),
        ("os", "For file operations (built-in)"),
        ("logging", "For logging (built-in)"),
    ]
    
    all_available = True
    
    for module, description in dependencies:
        try:
            __import__(module)
            print_test(f"{module} - {description}", True)
        except ImportError:
            print_test(f"{module} - {description}", False)
            all_available = False
    
    return all_available

def run_all_tests():
    """Run all tests."""
    print("\n" + "=" * 70)
    print("  AUTO-UPDATE SYSTEM TEST SUITE")
    print("=" * 70)
    print("\n  Testing auto-update system components...")
    
    results = []
    
    # Run tests
    results.append(("Module Imports", test_imports()))
    results.append(("Version File", test_version_file()))
    results.append(("Dependencies", test_dependencies()))
    results.append(("GitHub Connection", test_github_connection()))
    results.append(("Version Comparison", test_version_comparison()))
    results.append(("Update Check", test_update_check()))
    results.append(("Backup System", test_backup_creation()))
    
    # Summary
    print_header("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓" if result else "✗"
        print(f"  {status} {test_name}")
    
    print("\n" + "-" * 70)
    print(f"  Results: {passed}/{total} tests passed")
    print("-" * 70)
    
    if passed == total:
        print("\n  🎉 All tests passed! Auto-update system is ready.")
        print("\n  Next steps:")
        print("  1. Create a GitHub release with tag v1.1 (or higher)")
        print("  2. Attach a ZIP file with your application")
        print("  3. Test the update: python updater.py")
        print("  4. Integrate into your app: see example_integration.py")
    else:
        print("\n  ⚠ Some tests failed. Please fix the issues above.")
        print("\n  Common fixes:")
        print("  - Install dependencies: pip install requests")
        print("  - Create version.txt with current version")
        print("  - Check GitHub repository name and connectivity")
    
    print("\n" + "=" * 70)
    
    return passed == total

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nTests cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        sys.exit(1)
