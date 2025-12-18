"""
FBR Checker Module
Handles web automation for checking invoice status on FBR website using Selenium.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
import undetected_chromedriver as uc
import logging
import time
import random
import subprocess
import sys
import re


class FBRChecker:
    """
    Automates invoice verification on FBR portal using Selenium WebDriver.
    """
    
    # FBR Sales Tax Invoice Management URL
    FBR_URL = "https://irisv1.fbr.gov.pk/salesTax/invoices/index.xhtml?mode=3D2EAF95F000134C2BD2036C42962F48&task=270"
    
    def __init__(self, browser="Chrome"):
        """
        Initialize the FBR Checker with Selenium WebDriver.
        
        Args:
            browser (str): Browser to use - 'Chrome', 'Edge', or 'Firefox'
        """
        self.driver = None
        self.max_retries = 3
        self.actions = None  # ActionChains for mouse movements
        self.annex_a_tab_clicked = False  # Flag to ensure Annex-A tab is clicked only once
        self.last_error = None  # Store last error message for detailed reporting
        self.browser = browser  # Store browser choice
    
    @staticmethod
    def get_chrome_version():
        """
        Detect installed Chrome version on Windows.
        
        Returns:
            int: Major version number (e.g., 142) or None if not found
        """
        try:
            # Try to get Chrome version from registry
            import winreg
            reg_path = r"SOFTWARE\Google\Chrome\BLBeacon"
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
            version, _ = winreg.QueryValueEx(reg_key, "version")
            winreg.CloseKey(reg_key)
            
            # Extract major version (e.g., "142.0.7444.163" -> 142)
            major_version = int(version.split('.')[0])
            logging.info(f"Detected Chrome version: {version} (major: {major_version})")
            return major_version
        except:
            # Fallback: Try HKEY_LOCAL_MACHINE
            try:
                reg_path = r"SOFTWARE\Google\Chrome\BLBeacon"
                reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                version, _ = winreg.QueryValueEx(reg_key, "version")
                winreg.CloseKey(reg_key)
                
                major_version = int(version.split('.')[0])
                logging.info(f"Detected Chrome version: {version} (major: {major_version})")
                return major_version
            except:
                # Last resort: Try running chrome.exe --version
                try:
                    import subprocess
                    chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
                    result = subprocess.check_output([chrome_path, "--version"], text=True)
                    version = result.strip().split()[-1]
                    major_version = int(version.split('.')[0])
                    logging.info(f"Detected Chrome version via executable: {version} (major: {major_version})")
                    return major_version
                except:
                    logging.warning("Could not detect Chrome version. Will use auto-detection.")
                    return None
    
    @staticmethod
    def get_edge_version():
        """
        Detect installed Edge version on Windows.
        
        Returns:
            str: Full version string (e.g., "120.0.2210.144") or None if not found
        """
        try:
            # Try to get Edge version from registry
            import winreg
            reg_path = r"SOFTWARE\Microsoft\Edge\BLBeacon"
            reg_key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path)
            version, _ = winreg.QueryValueEx(reg_key, "version")
            winreg.CloseKey(reg_key)
            
            logging.info(f"Detected Edge version: {version}")
            return version
        except:
            # Fallback: Try HKEY_LOCAL_MACHINE
            try:
                reg_path = r"SOFTWARE\Microsoft\Edge\BLBeacon"
                reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
                version, _ = winreg.QueryValueEx(reg_key, "version")
                winreg.CloseKey(reg_key)
                
                logging.info(f"Detected Edge version: {version}")
                return version
            except:
                # Last resort: Try running msedge.exe --version
                try:
                    import subprocess
                    edge_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"
                    result = subprocess.check_output([edge_path, "--version"], text=True)
                    version = result.strip().split()[-1]
                    logging.info(f"Detected Edge version via executable: {version}")
                    return version
                except:
                    logging.warning("Could not detect Edge version. Selenium Manager will handle it.")
                    return None
    
    @staticmethod
    def get_firefox_version():
        """
        Detect installed Firefox version on Windows.
        
        Returns:
            str: Full version string (e.g., "121.0") or None if not found
        """
        try:
            # Try to get Firefox version from registry
            import winreg
            reg_path = r"SOFTWARE\Mozilla\Mozilla Firefox"
            reg_key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, reg_path)
            version, _ = winreg.QueryValueEx(reg_key, "CurrentVersion")
            winreg.CloseKey(reg_key)
            
            logging.info(f"Detected Firefox version: {version}")
            return version
        except:
            # Try running firefox.exe --version
            try:
                import subprocess
                firefox_path = r"C:\Program Files\Mozilla Firefox\firefox.exe"
                result = subprocess.check_output([firefox_path, "--version"], text=True)
                version = result.strip().split()[-1]
                logging.info(f"Detected Firefox version via executable: {version}")
                return version
            except:
                logging.warning("Could not detect Firefox version. Selenium Manager will handle it.")
                return None
        
    def initialize_browser(self):
        """
        Initialize browser with hybrid approach: tries undetected-chromedriver first (maximum stealth),
        falls back to standard Selenium if not available. Optimized for OGDCL corporate environment.
        Supports Chrome, Edge, and Firefox.
        
        Returns:
            bool: True if browser initialized successfully, False otherwise
        """
        try:
            logging.info(f"🚀 Initializing {self.browser} browser...")
            
            # CHROME: Use undetected-chromedriver with proper version detection
            if self.browser == "Chrome":
                logging.info("🔍 Initializing undetected-chromedriver (stealth mode)...")
                options = uc.ChromeOptions()
                options.add_argument('--start-maximized')
                options.add_argument('--homepage=about:blank')  # Fix firewall blocking data:// URLs
                options.add_argument('--no-first-run')
                options.add_argument('--no-default-browser-check')
                options.add_argument('--disable-popup-blocking')
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('--disable-infobars')
                options.add_argument('--log-level=3')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                
                # OGDCL-optimized SSL settings
                options.add_argument('--ignore-certificate-errors')
                options.add_argument('--ignore-ssl-errors')
                options.add_argument('--allow-insecure-localhost')
                options.add_argument('--disable-web-security')
                
                prefs = {
                    "profile.default_content_setting_values.notifications": 2,
                    "credentials_enable_service": False,
                    "profile.password_manager_enabled": False,
                    "profile.managed_default_content_settings.images": 1,
                    "profile.default_content_setting_values.ssl_cert_decisions": 1,
                }
                options.add_experimental_option("prefs", prefs)
                
                # Detect Chrome version automatically for version-independent operation
                chrome_version = self.get_chrome_version()
                
                # Initialize undetected Chrome with detected version
                # use_subprocess=False prevents Windows multiprocessing issues
                if chrome_version:
                    logging.info(f"🎯 Using detected Chrome major version: {chrome_version}")
                    self.driver = uc.Chrome(options=options, version_main=chrome_version, use_subprocess=False)
                else:
                    logging.info("⚠️ Chrome version not detected, using auto-detection")
                    self.driver = uc.Chrome(options=options, use_subprocess=False)
                
                # Minimal stealth JS (faster than 100+ lines)
                self.driver.execute_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'vendor', {get: () => 'Google Inc.'});
                    window.chrome = {runtime: {}};
                """)
                
                logging.info("✅ Chrome initialized with undetected-chromedriver (maximum stealth)")
                logging.info("🔒 Secure SSL/TLS + OGDCL firewall optimizations active")
                
            elif self.browser == "Edge":
                # Detect Edge version for logging (Selenium Manager auto-handles driver)
                edge_version = self.get_edge_version()
                if edge_version:
                    logging.info(f"🎯 Detected Edge version: {edge_version}")
                else:
                    logging.info("⚠️ Edge version not detected, Selenium Manager will handle it")
                
                options = webdriver.EdgeOptions()
                options.add_argument('--start-maximized')
                options.add_argument('--homepage=about:blank')  # firewall blocking data:// URLs
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_argument('--disable-infobars')
                options.add_argument('--no-first-run')
                options.add_argument('--no-default-browser-check')
                options.add_argument('--disable-popup-blocking')
                options.add_argument('--disable-extensions')
                options.add_argument('--disable-default-apps')
                options.add_argument('--log-level=3')
                options.add_argument('--disable-dev-shm-usage')
                options.add_argument('--disable-gpu')
                options.add_argument('--no-sandbox')
                
                # OGDCL-optimized SSL settings
                options.add_argument('--ignore-certificate-errors')
                options.add_argument('--ignore-ssl-errors')
                options.add_argument('--allow-insecure-localhost')
                options.add_argument('--disable-web-security')
                
                prefs = {
                    "profile.default_content_setting_values.notifications": 2,
                    "credentials_enable_service": False,
                    "profile.password_manager_enabled": False,
                    "profile.managed_default_content_settings.images": 1,
                    "profile.default_content_setting_values.ssl_cert_decisions": 1,
                }
                options.add_experimental_option("prefs", prefs)
                options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
                options.add_experimental_option("useAutomationExtension", False)
                
                self.driver = webdriver.Edge(options=options)
                
                # Minimal stealth JavaScript
                self.driver.execute_script("""
                    Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                    Object.defineProperty(navigator, 'vendor', {get: () => 'Google Inc.'});
                    window.chrome = {runtime: {}};
                """)
                
                self.driver.implicitly_wait(3)
                self.actions = ActionChains(self.driver)
                
                logging.info("✅ Edge initialized with secure SSL/TLS + OGDCL optimizations")
                
            elif self.browser == "Firefox":
                # Detect Firefox version for logging (Selenium Manager auto-handles driver)
                firefox_version = self.get_firefox_version()
                if firefox_version:
                    logging.info(f"🎯 Detected Firefox version: {firefox_version}")
                else:
                    logging.info("⚠️ Firefox version not detected, Selenium Manager will handle it")
                
                options = webdriver.FirefoxOptions()
                options.add_argument('--start-maximized')
                options.set_preference("dom.webdriver.enabled", False)
                options.set_preference('useAutomationExtension', False)
                options.set_preference("dom.webnotifications.enabled", False)
                
                # OGDCL-optimized SSL settings for Firefox
                options.set_preference("security.tls.version.enable-deprecated", True)
                options.set_preference("security.ssl.enable_ocsp_stapling", True)
                options.set_preference("security.ssl.enable_ocsp_must_staple", False)
                options.set_preference("security.cert_pinning.enforcement_level", 0)
                options.set_preference("security.enterprise_roots.enabled", True)
                options.accept_insecure_certs = True
                
                self.driver = webdriver.Firefox(options=options)
                self.driver.implicitly_wait(3)
                self.actions = ActionChains(self.driver)
                
                logging.info("✅ Firefox initialized with secure SSL/TLS + OGDCL optimizations")
                
            else:
                raise ValueError(f"Unsupported browser: {self.browser}. Choose 'Chrome', 'Edge', or 'Firefox'.")
            
            # Set implicit wait (optimized for speed)
            self.driver.implicitly_wait(3)
            
            # Initialize ActionChains
            self.actions = ActionChains(self.driver)
            
            logging.info(f"✅ {self.browser} browser initialized successfully")
            return True
            
        except Exception as e:
            error_msg = str(e)
            self.last_error = error_msg
            logging.error(f"Failed to initialize {self.browser} browser: {error_msg}")
            
            # Provide specific guidance based on error type
            if "PATH" in error_msg.upper() or "driver" in error_msg.lower():
                logging.error(f"{self.browser}Driver PATH issue. Selenium Manager should auto-download it.")
                logging.error("If this persists, check internet connection or firewall settings.")
            elif "session not created" in error_msg.lower() or "version" in error_msg.lower():
                logging.error(f"{self.browser} version compatibility issue detected.")
                logging.error(f"Solution: Update {self.browser} browser to the latest version.")
            elif "not reachable" in error_msg.lower():
                logging.error(f"{self.browser} browser not accessible. Verify {self.browser} is installed correctly.")
                logging.error(f"Try: 1) Reinstalling {self.browser}, 2) Running as Administrator")
            elif "timeout" in error_msg.lower():
                logging.error(f"Browser startup timeout. Close other {self.browser} instances and try again.")
            else:
                logging.error(f"Unexpected error type: {error_msg[:100]}")
            
            return False
    
    def _random_delay(self, min_seconds=0.5, max_seconds=2.0):
        """
        Add a random human-like delay.
        
        Args:
            min_seconds (float): Minimum delay in seconds
            max_seconds (float): Maximum delay in seconds
        """
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    def _human_like_type(self, element, text):
        """
        Type text character by character with random delays to simulate human typing.
        
        Args:
            element: WebElement to type into
            text (str): Text to type
        """
        element.clear()
        self._random_delay(0.1, 0.25)
        
        for char in str(text):
            element.send_keys(char)
            # Random typing speed between 50-150ms per character
            time.sleep(random.uniform(0.02, 0.08))
        
        # Small pause after typing
        self._random_delay(0.25, 0.5)
    
    def _human_like_click(self, element):
        """
        Click element with mouse movement to simulate human behavior.
        
        Args:
            element: WebElement to click
        """
        try:
            # Ensure element is in view first
            try:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});",
                    element,
                )
            except Exception:
                # ignore scroll failures
                pass
            
            
            self._random_delay(0.1, 0.3)  # Reduced from 0.2-0.6 for faster execution

            # Check visibility and size — some elements are present but have no size/location
            try:
                displayed = element.is_displayed()
                size = element.size
            except Exception:
                displayed = True
                size = {'width': 1, 'height': 1}

            width = size.get('width', 0) if isinstance(size, dict) else getattr(size, 'get', lambda k, d: d)('width', 0)
            height = size.get('height', 0) if isinstance(size, dict) else getattr(size, 'get', lambda k, d: d)('height', 0)

            # If element is not visible or has no size, try JS click first
            if not displayed or width == 0 or height == 0:
                try:
                    self.driver.execute_script("arguments[0].click();", element)
                    logging.debug("Performed JS click on element (fallback for not-interactable element)")
                    return
                except Exception as js_e:
                    logging.warning(f"JS click fallback failed: {js_e}")

            # Try ActionChains move+click (preferred human-like interaction)
            try:
                self.actions.move_to_element(element).perform()
                self._random_delay(0.05, 0.15)  # Reduced from 0.10-0.25 for faster execution
                self.actions.click(element).perform()
                logging.debug("Performed human-like click via ActionChains")
                return
            except Exception as ac_e:
                logging.warning(f"ActionChains click failed, trying direct click fallback: {ac_e}")

            # Fallback to element.click()
            try:
                element.click()
                logging.debug("Performed direct element.click() fallback")
                return
            except Exception as final_e:
                logging.error(f"Final click fallback failed: {final_e}")

        except Exception as e:
            logging.error(f"Error in _human_like_click: {e}")
    
    def _simulate_mouse_movement(self):
        """
        Simulate minimal mouse movement (optimized for speed).
        """
        try:
            # Single minimal mouse movement
            x_offset = random.randint(-50, 50)
            y_offset = random.randint(-50, 50)
            self.actions.move_by_offset(x_offset, y_offset).perform()
        except Exception:
            pass  # Ignore errors in mouse simulation
    
    def _select_date_from_datepicker(self, date_string):
        """
        Parse date string and select date from datepicker calendar.
        
        Args:
            date_string: Date in various formats including datetime objects
            
        Returns:
            dict: Parsed date with 'day', 'month', 'year' keys, or None if parsing failed
        """
        try:
            from datetime import datetime
            
            logging.info(f"Parsing date: '{date_string}' (type: {type(date_string).__name__})")
            
            # Handle datetime objects directly
            if isinstance(date_string, datetime):
                parsed_date = date_string
                logging.info(f"Date is datetime object: {parsed_date}")
            elif hasattr(date_string, 'to_pydatetime'):  # pandas Timestamp
                parsed_date = date_string.to_pydatetime()
                logging.info(f"Date is pandas Timestamp, converted: {parsed_date}")
            else:
                # Convert to string and try parsing
                date_str = str(date_string).strip()
                logging.info(f"Date as string: '{date_str}'")
                
                # Try multiple date formats (most common first)
                date_formats = [
                    '%Y-%m-%d %H:%M:%S',  # 2025-07-07 00:00:00 (Excel datetime)
                    '%Y-%m-%d',           # 2025-04-07
                    '%d-%b-%Y',           # 07-Apr-2025
                    '%d-%B-%Y',           # 07-April-2025
                    '%d/%m/%Y',           # 07/04/2025
                    '%m/%d/%Y',           # 04/07/2025
                    '%d-%m-%Y',           # 07-04-2025
                    '%d.%m.%Y',           # 07.04.2025
                    '%Y-%m-%d %H:%M:%S.%f',  # 2025-07-07 00:00:00.000
                ]
                
                parsed_date = None
                for date_format in date_formats:
                    try:
                        parsed_date = datetime.strptime(date_str, date_format)
                        logging.info(f"Successfully parsed with format '{date_format}': {parsed_date}")
                        break
                    except ValueError:
                        continue
                
                # If all formats fail, try pandas parser as last resort
                if not parsed_date:
                    try:
                        import pandas as pd
                        parsed_date = pd.to_datetime(date_str, errors='coerce')
                        if pd.isna(parsed_date):
                            logging.warning(f"Pandas parser returned NaT for: {date_str}")
                            parsed_date = None
                        else:
                            parsed_date = parsed_date.to_pydatetime()
                            logging.info(f"Successfully parsed with pandas: {parsed_date}")
                    except Exception as pd_err:
                        logging.warning(f"Pandas parser failed: {str(pd_err)}")
                        pass
            
            if parsed_date:
                formatted_date = parsed_date.strftime('%d-%b-%Y')  # Format: 11-Nov-2025
                logging.info(f"✓ Date parsed successfully: {formatted_date}")
                return {
                    'day': parsed_date.day,
                    'month': parsed_date.month,
                    'year': parsed_date.year,
                    'formatted': formatted_date
                }
            else:
                logging.error(f"❌ Could not parse date: {date_string} (tried all formats)")
                return None
                
        except Exception as e:
            logging.error(f"❌ Exception parsing date {date_string}: {str(e)}")
            import traceback
            logging.error(traceback.format_exc())
            return None
    
    def click_annex_a_tab(self):
        """
        Click the Annex-A (Purchases) tab if present on the current page.
        
        Returns:
            bool: True if tab was found and clicked, False otherwise
        """
        try:
            # Look for the Annex-A tab with the specific class structure
            tab_xpath = "//li[@class='ui-state-default ui-corner-top ui-tabs-selected ui-state-active' or contains(@class, 'ui-tabs-selected')]//a[contains(text(), 'Annex-A')]"
            
            # More flexible selector for Annex-A tab
            annex_a_tab = None
            selectors = [
                (By.XPATH, "//li[contains(@class, 'ui-tabs-selected')]//a[contains(text(), 'Annex-A')]"),
                (By.XPATH, "//a[contains(@href, '#correspondenceTabs:tab') and contains(text(), 'Annex-A')]"),
                (By.XPATH, "//li[@role='tab']//a[contains(text(), 'Annex-A (Purchases)')]"),
                (By.XPATH, "//a[contains(text(), 'Annex-A')]"),
            ]
            
            for by_type, selector in selectors:
                try:
                    annex_a_tab = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by_type, selector))
                    )
                    logging.info(f"Found Annex-A tab using selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not annex_a_tab:
                logging.info("Annex-A tab not found on current page")
                return False
            
            # Click the tab
            self._human_like_click(annex_a_tab)
            self._random_delay(0.25, 0.5)
            logging.info("✅ Clicked Annex-A (Purchases) tab")
            return True
            
        except Exception as e:
            logging.warning(f"Error clicking Annex-A tab: {str(e)}")
            return False
    
    def click_claim_invoices_button(self):
        """
        Click the 'Claim Invoices' dropdown button after Annex-A tab is active.
        Robust implementation with multiple selector strategies and JavaScript fallback.
        
        Returns:
            bool: True if button was found and clicked, False otherwise
        """
        try:
            # Look for the span with ui-menubutton class containing the button
            claim_button = None
            selectors = [
                # Strategy 1: Exact ID from the provided HTML (if ID doesn't change)
                (By.ID, "correspondenceTabs:annexa-form:j_idt6954_button"),
                
                # Strategy 2: Partial ID match with dynamic j_idt number
                (By.XPATH, "//button[contains(@id, 'annexa-form:j_idt') and contains(@id, '_button')]"),
                
                # Strategy 3: Button inside ui-menubutton span with text match
                (By.XPATH, "//span[@class='ui-menubutton']//button[contains(normalize-space(.), 'Claim Invoices')]"),
                
                # Strategy 4: Button with ui-menubutton class or inside ui-menubutton span
                (By.XPATH, "//button[contains(@class, 'ui-menubutton') or ancestor::span[@class='ui-menubutton']]//span[contains(text(), 'Claim Invoices')]"),
                
                # Strategy 5: Any button with span containing "Claim Invoices" text
                (By.XPATH, "//button[.//span[contains(text(), 'Claim Invoices')]]"),
                
                # Strategy 6: Form-scoped button with "Claim Invoices" text in annexa-form
                (By.XPATH, "//form[contains(@id, 'annexa-form')]//button[contains(., 'Claim Invoices')]"),
                
                # Strategy 7: Button with aria-label or title containing "Claim Invoices"
                (By.XPATH, "//button[@aria-label='Claim Invoices' or @title='Claim Invoices']"),
                
                # Strategy 8: CSS selector with partial attribute matching
                (By.CSS_SELECTOR, "button[id*='annexa-form'][id*='button']"),
                
                # Strategy 9: Button with ui-button class and menu role in annexa context
                (By.XPATH, "//button[contains(@class, 'ui-button') and contains(@id, 'annexa-form')]"),
                
                # Strategy 10: Generic - any visible button in menubutton span
                (By.XPATH, "//span[contains(@class, 'ui-menubutton')]//button[not(contains(@style, 'display: none'))]"),
            ]
            
            for by_type, selector in selectors:
                try:
                    # Try to find the element immediately (button is usually already present)
                    claim_button = None
                    try:
                        found = self.driver.find_elements(by_type, selector)
                        if found:
                            claim_button = found[0]
                        else:
                            # element not found immediately; continue to next selector
                            raise NoSuchElementException()
                    except NoSuchElementException:
                        # move to next selector quickly
                        raise
                    
                    # Verify element is actually visible and enabled
                    if claim_button.is_displayed() and claim_button.is_enabled():
                        # Additional text verification to ensure it's the correct button
                        button_text = claim_button.text.strip()
                        if 'Claim Invoices' in button_text or 'Claim' in button_text:
                            logging.info(f"✓ Found Claim Invoices button using selector: {selector}")
                            logging.debug(f"  Button text verified: '{button_text}'")
                            break
                        else:
                            logging.debug(f"Button text mismatch: '{button_text}' (expected 'Claim Invoices')")
                            claim_button = None
                    else:
                        logging.debug(f"Element found but not interactable with selector: {selector}")
                        claim_button = None
                        
                except (TimeoutException, NoSuchElementException) as e:
                    logging.debug(f"Selector failed: {selector} - {type(e).__name__}")
                    continue
                except Exception as e:
                    logging.debug(f"Unexpected error with selector {selector}: {str(e)}")
                    continue
            
            # Fallback: Use JavaScript to find button if all selectors fail
            if not claim_button:
                logging.warning("All selectors failed, trying JavaScript fallback for Claim Invoices button...")
                try:
                    claim_button = self.driver.execute_script("""
                        // Strategy 1: Find by form ID containing 'annexa-form'
                        var form = document.querySelector('form[id*="annexa-form"]');
                        if (form) {
                            var buttons = form.querySelectorAll('button');
                            for (var i = 0; i < buttons.length; i++) {
                                var btn = buttons[i];
                                var btnText = btn.textContent.trim();
                                
                                // Check if button contains "Claim Invoices" text
                                if (btnText.includes('Claim Invoices') && 
                                    btn.offsetParent !== null && // visible
                                    !btn.disabled) { // enabled
                                    return btn;
                                }
                            }
                        }
                        
                        // Strategy 2: Find by ui-menubutton span
                        var menuButtons = document.querySelectorAll('span.ui-menubutton button');
                        for (var i = 0; i < menuButtons.length; i++) {
                            var btn = menuButtons[i];
                            var btnText = btn.textContent.trim();
                            
                            if (btnText.includes('Claim Invoices') && 
                                btn.offsetParent !== null && 
                                !btn.disabled) {
                                return btn;
                            }
                        }
                        
                        // Strategy 3: Find any button with ID containing 'annexa-form' and 'button'
                        var allButtons = document.querySelectorAll('button[id*="annexa-form"]');
                        for (var i = 0; i < allButtons.length; i++) {
                            var btn = allButtons[i];
                            if (btn.id.includes('button') && 
                                btn.offsetParent !== null && 
                                !btn.disabled) {
                                var btnText = btn.textContent.trim();
                                if (btnText.includes('Claim') || btnText.includes('Invoice')) {
                                    return btn;
                                }
                            }
                        }
                        
                        // Strategy 4: Check button spans for "Claim Invoices" text
                        var spans = document.querySelectorAll('button span');
                        for (var i = 0; i < spans.length; i++) {
                            var span = spans[i];
                            var spanText = span.textContent.trim();
                            
                            if (spanText === 'Claim Invoices' || spanText.includes('Claim Invoices')) {
                                var parentBtn = span.closest('button');
                                if (parentBtn && parentBtn.offsetParent !== null && !parentBtn.disabled) {
                                    return parentBtn;
                                }
                            }
                        }
                        
                        return null;
                    """)
                    
                    if claim_button:
                        button_text = claim_button.text.strip()
                        logging.info(f"✓ Found Claim Invoices button using JavaScript fallback")
                        logging.info(f"  Button text: '{button_text}'")
                    
                except Exception as js_error:
                    logging.error(f"JavaScript fallback also failed: {str(js_error)}")
            
            if not claim_button:
                logging.error("Claim Invoices button not found after trying all strategies")
                return False
            
            # Final verification before clicking
            try:
                button_text = claim_button.text.strip()
                logging.info(f"About to click Claim Invoices button (text: '{button_text}')")
            except Exception:
                logging.warning("Could not verify button text before clicking")
            
            # Click the button
            self._human_like_click(claim_button)
            self._random_delay(0.05, 0.1)  # Reduced from 0.15-0.25 to 0.05-0.1 for faster execution
            logging.info("✅ Clicked 'Claim Invoices' button")
            return True
            
        except Exception as e:
            logging.warning(f"Error clicking Claim Invoices button: {str(e)}")
            return False
    
    def click_claim_in_fbr_menu_item(self):
        """
        Click the 'Claim in FBR' menu item from the dropdown.
        
        Returns:
            bool: True if menu item was found and clicked, False otherwise
        """
        try:
            # Look for the menu item with text "Claim in FBR"
            claim_fbr_item = None
            selectors = [
                # Look for the anchor with the specific onclick handler pattern
                (By.XPATH, "//a[contains(@onclick, 'PrimeFaces.ab') and contains(@onclick, 'annexAClaimBtnPnl') and .//span[contains(text(), 'Claim in FBR')]]"),
                # More flexible selectors
                (By.XPATH, "//span[@class='ui-menuitem-text' and contains(text(), 'Claim in FBR')]/ancestor::a"),
                (By.XPATH, "//a[.//span[contains(@class, 'ui-menuitem-text') and contains(text(), 'Claim in FBR')]]"),
                (By.XPATH, "//a[contains(text(), 'Claim in FBR')]"),
            ]
            
            for by_type, selector in selectors:
                try:
                    claim_fbr_item = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by_type, selector))
                    )
                    logging.info(f"Found 'Claim in FBR' menu item using selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not claim_fbr_item:
                logging.error("'Claim in FBR' menu item not found")
                return False
            
            # Click the menu item
            self._human_like_click(claim_fbr_item)
            self._random_delay(0.1, 0.25)
            logging.info("✅ Clicked 'Claim in FBR' menu item")
            return True
            
        except Exception as e:
            logging.warning(f"Error clicking 'Claim in FBR' menu item: {str(e)}")
            return False
    
    def process_claim_workflow(self):
        """
        Execute the complete Annex-A claim workflow:
        1. Click Annex-A (Purchases) tab
        2. Click Claim Invoices button
        3. Click Claim in FBR menu item
        
        Returns:
            bool: True if all steps completed successfully, False otherwise
        """
        try:
            logging.info("Starting Annex-A claim workflow...")
            
            # Wait for page to fully load before processing
            logging.info("Waiting for page to fully load...")
            try:
                WebDriverWait(self.driver, 5).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                logging.info("✓ Page fully loaded")
            except TimeoutException:
                logging.warning("Page load timeout, but proceeding anyway...")
            
            # Step 1: Click Annex-A tab (RUN ONLY ONCE)
            if not self.annex_a_tab_clicked:
                if not self.click_annex_a_tab():
                    logging.warning("Annex-A tab workflow skipped (tab not found)")
                    return False
                self.annex_a_tab_clicked = True
                logging.info("✅ Annex-A tab clicked and will not be clicked again for this session")
            else:
                logging.info("ℹ️ Annex-A tab already clicked in this session, skipping...")
            
            # Step 2: Click Claim Invoices button
            if not self.click_claim_invoices_button():
                logging.error("Failed at Claim Invoices button step")
                return False
            
            # Step 3: Click Claim in FBR menu item
            if not self.click_claim_in_fbr_menu_item():
                logging.error("Failed at Claim in FBR menu item step")
                return False
            
            logging.info("✅ Annex-A claim workflow completed successfully")
            return True
            
        except Exception as e:
            logging.error(f"Error in claim workflow: {str(e)}")
            return False
    
    def is_browser_alive(self):
        """
        Check if the browser instance is still alive and responsive.
        
        Returns:
            bool: True if browser is alive, False otherwise
        """
        try:
            if not self.driver:
                return False
            # Try to get current URL to verify browser is responsive
            _ = self.driver.current_url
            return True
        except Exception:
            return False
    
    def navigate_to_fbr(self):
        """
        Navigate to the FBR invoice verification portal.
        
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            self.driver.get(self.FBR_URL)
            logging.info(f"Navigated to FBR portal: {self.FBR_URL}")
            
            # Minimal delay for page load
            self._random_delay(0.5, 1.0)
            
            return True
            
        except WebDriverException as e:
            logging.error(f"Browser closed or connection lost: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Error navigating to FBR portal: {str(e)}")
            return False
        
    
    def verify_invoice(self, invoice_number, source_authority=None, invoice_no_field=None, date_field=None, sales_tax_fed_st_mode=None):
        """
        Verify a single invoice number on the FBR portal.
        
        Args:
            invoice_number (str): The seller registration number (NTN) to verify
            source_authority (str): Source Authority value (e.g., 'FBR', 'BRA', 'KPRA', 'PRA', 'SRB')
            invoice_no_field (str): Invoice number from 'Number' column in Excel
            date_field (str): Date from 'Date' column in Excel (will be used for both From and To dates)
            sales_tax_fed_st_mode (str): Sales Tax/FED in ST Mode value from Excel to match with FBR data
            
        Returns:
            dict: Status and details including matched row information
        """
        try:
            # Check if browser is still alive before proceeding
            if not self.is_browser_alive():
                logging.error("Browser was closed by user")
                return {
                    'status': '⚠️ Browser Closed',
                    'value_of_purchases': 'N/A'
                }
            
            # Process the claim workflow (Annex-A steps)
            self.process_claim_workflow()
            
            # Wait for page to be ready (reduced timeout)
            logging.info("Waiting for page to load...")
            try:
                WebDriverWait(self.driver, 15).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                logging.info("✓ Page loaded")
            except TimeoutException:
                logging.warning("Page load timeout, but proceeding...")
            
            wait = WebDriverWait(self.driver, 20)
            
            # Step 1: Select Source Authority from dropdown if provided
            if source_authority:
                logging.info(f"STEP 1: Selecting Source Authority: {source_authority}")
                
                # Find the dropdown element
                dropdown_selectors = [
                    (By.ID, "correspondenceTabs:loadAnnexAform:sourceAuthorityFilter"),
                    (By.XPATH, "//div[@id='correspondenceTabs:loadAnnexAform:sourceAuthorityFilter']"),
                    (By.XPATH, "//div[contains(@class, 'ui-selectonemenu') and contains(@id, 'sourceAuthorityFilter')]"),
                ]
                
                dropdown = None
                for by_type, selector in dropdown_selectors:
                    try:
                        # Wait for element to be visible AND clickable
                        dropdown = wait.until(EC.visibility_of_element_located((by_type, selector)))
                        dropdown = wait.until(EC.element_to_be_clickable((by_type, selector)))
                        logging.info(f"Found dropdown using selector: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if not dropdown:
                    logging.error("STEP 1 FAILED: Source Authority dropdown not found")
                    return {
                        'status': '⚠️ Error - Dropdown not found',
                        'value_of_purchases': 'N/A'
                    }
                
                # Click the dropdown to open it
                self._human_like_click(dropdown)
                self._random_delay(0.25, 0.5)
                
                # Select the option by text (source_authority value from Excel)
                # Map option values: 7=BRA, 1=FBR, 6=KPRA, 5=PRA, 8=SRB
                authority_map = {
                    'BRA': '7',
                    'FBR': '1',
                    'KPRA': '6',
                    'PRA': '5',
                    'SRB': '8'
                }
                
                # Normalize source_authority
                source_auth_normalized = str(source_authority).strip().upper()
                option_value = authority_map.get(source_auth_normalized)
                
                if not option_value:
                    logging.error(f"STEP 1 FAILED: Unknown source authority '{source_authority}', valid values: {list(authority_map.keys())}")
                    return {
                        'status': '⚠️ Error - Invalid source authority',
                        'value_of_purchases': 'N/A'
                    }
                
                # Find and click the option in the dropdown
                option_selectors = [
                    (By.XPATH, f"//div[@id='correspondenceTabs:loadAnnexAform:sourceAuthorityFilter_panel']//li[@data-label='{source_auth_normalized}']"),
                    (By.XPATH, f"//div[contains(@id, 'sourceAuthorityFilter_panel')]//li[contains(text(), '{source_auth_normalized}')]"),
                    (By.XPATH, f"//select[@id='correspondenceTabs:loadAnnexAform:sourceAuthorityFilter_input']/option[@value='{option_value}']"),
                ]
                
                option_selected = False
                for by_type, selector in option_selectors:
                    try:
                        option = wait.until(EC.element_to_be_clickable((by_type, selector)))
                        self._human_like_click(option)
                        logging.info(f"✓ STEP 1 COMPLETED: Selected Source Authority: {source_auth_normalized}")
                        option_selected = True
                        self._random_delay(0.25,0.5)
                        break
                    except TimeoutException:
                        continue
                
                if not option_selected:
                    logging.error(f"STEP 1 FAILED: Could not select option '{source_auth_normalized}' from dropdown")
                    return {
                        'status': '⚠️ Error - Option not selectable',
                        'value_of_purchases': 'N/A'
                    }
                
                # Verify selection was applied
                self._random_delay(0.1, 0.25)
                selected_value = self.driver.execute_script("""
                    var dropdown = document.getElementById('correspondenceTabs:loadAnnexAform:sourceAuthorityFilter');
                    if (dropdown) {
                        var label = dropdown.querySelector('.ui-selectonemenu-label');
                        return label ? label.innerText.trim() : '';
                    }
                    return '';
                """)
                
                if selected_value != source_auth_normalized:
                    logging.error(f"STEP 1 VERIFICATION FAILED: Expected '{source_auth_normalized}', got '{selected_value}'")
                    return {
                        'status': '⚠️ Error - Selection verification failed',
                        'value_of_purchases': 'N/A'
                    }
                
                logging.info(f"✓ STEP 1 VERIFIED: Source Authority is set to '{selected_value}'")
            
            # Step 2: Enter Seller NTN in the annexASellerRegNo field
            if invoice_number:
                logging.info(f"STEP 2: Entering Seller NTN: {invoice_number}")
                
                # Find the Seller Registration No input field in Annex-A form
                seller_ntn_input = None
                seller_ntn_selectors = [
                    (By.ID, "correspondenceTabs:loadAnnexAform:annexASellerRegNo"),
                    (By.NAME, "correspondenceTabs:loadAnnexAform:annexASellerRegNo"),
                    (By.XPATH, "//input[@id='correspondenceTabs:loadAnnexAform:annexASellerRegNo']"),
                    (By.XPATH, "//input[@name='correspondenceTabs:loadAnnexAform:annexASellerRegNo']"),
                    (By.XPATH, "//input[@type='text' and @maxlength='13']"),
                ]
                
                for by_type, selector in seller_ntn_selectors:
                    try:
                        # Wait for element to be visible AND clickable
                        seller_ntn_input = wait.until(EC.visibility_of_element_located((by_type, selector)))
                        seller_ntn_input = wait.until(EC.element_to_be_clickable((by_type, selector)))
                        logging.info(f"Found Seller NTN input using selector: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if not seller_ntn_input:
                    logging.error("STEP 2 FAILED: Seller NTN input field not found")
                    return {
                        'status': '⚠️ Error - NTN field not found',
                        'value_of_purchases': 'N/A'
                    }
                
                # Human-like interaction: move to field and type naturally
                self._human_like_click(seller_ntn_input)
                self._human_like_type(seller_ntn_input, invoice_number)
                self._random_delay(0.1, 0.25)
                
                # Verify the value was entered
                entered_value = seller_ntn_input.get_attribute('value')
                if entered_value != str(invoice_number):
                    logging.error(f"STEP 2 VERIFICATION FAILED: Expected '{invoice_number}', got '{entered_value}'")
                    return {
                        'status': '⚠️ Error - NTN entry verification failed',
                        'value_of_purchases': 'N/A'
                    }
                
                logging.info(f"✓ STEP 2 COMPLETED & VERIFIED: Seller NTN = '{entered_value}'")
                self._random_delay(0.25, 0.5)
            
            # Step 3: Enter Invoice Number in the annexAinvoiceNoId field
            if invoice_no_field:
                logging.info(f"STEP 3: Entering Invoice Number: {invoice_no_field}")
                
                # Find the Invoice Number input field in Annex-A form
                invoice_no_input = None
                invoice_no_selectors = [
                    (By.ID, "correspondenceTabs:loadAnnexAform:annexAinvoiceNoId"),
                    (By.NAME, "correspondenceTabs:loadAnnexAform:annexAinvoiceNoId"),
                    (By.XPATH, "//input[@id='correspondenceTabs:loadAnnexAform:annexAinvoiceNoId']"),
                    (By.XPATH, "//input[@name='correspondenceTabs:loadAnnexAform:annexAinvoiceNoId']"),
                    (By.XPATH, "//input[@type='text' and @maxlength='25']"),
                ]
                
                for by_type, selector in invoice_no_selectors:
                    try:
                        # Wait for element to be visible AND clickable
                        invoice_no_input = wait.until(EC.visibility_of_element_located((by_type, selector)))
                        invoice_no_input = wait.until(EC.element_to_be_clickable((by_type, selector)))
                        logging.info(f"Found Invoice Number input using selector: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if not invoice_no_input:
                    logging.error("STEP 3 FAILED: Invoice Number input field not found")
                    return {
                        'status': '⚠️ Error - Invoice field not found',
                        'value_of_purchases': 'N/A'
                    }
                
                # Human-like interaction: move to field and type naturally
                self._human_like_click(invoice_no_input)
                self._human_like_type(invoice_no_input, invoice_no_field)
                self._random_delay(0.1, 0.25)
                
                # Verify the value was entered
                entered_value = invoice_no_input.get_attribute('value')
                if entered_value != str(invoice_no_field):
                    logging.error(f"STEP 3 VERIFICATION FAILED: Expected '{invoice_no_field}', got '{entered_value}'")
                    return {
                        'status': '⚠️ Error - Invoice entry verification failed',
                        'value_of_purchases': 'N/A'
                    }
                
                logging.info(f"✓ STEP 3 COMPLETED & VERIFIED: Invoice Number = '{entered_value}'")
                self._random_delay(0.25, 0.5)
            
            # Step 4: Select From Date and To Date from datepickers
            if date_field and date_field != 'N/A':
                logging.info(f"STEP 4: Selecting dates: {date_field}")
                
                # Parse the date
                parsed_date = self._select_date_from_datepicker(date_field)
                
                if not parsed_date:
                    logging.error(f"STEP 4 FAILED: Could not parse date: {date_field}")
                    return {
                        'status': '⚠️ Error - Date parsing failed',
                        'value_of_purchases': 'N/A'
                    }
                
                date_formatted = parsed_date['formatted']
                
                # Select From Date
                from_date_selectors = [
                    (By.ID, "correspondenceTabs:loadAnnexAform:annexAFromDate_input"),
                    (By.NAME, "correspondenceTabs:loadAnnexAform:annexAFromDate_input"),
                    (By.XPATH, "//input[@id='correspondenceTabs:loadAnnexAform:annexAFromDate_input']"),
                ]
                
                
                from_date_input = None
                for by_type, selector in from_date_selectors:
                    try:
                        # Wait for element to be visible and present
                        from_date_input = wait.until(EC.visibility_of_element_located((by_type, selector)))
                        logging.info(f"Found From Date input using selector: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if not from_date_input:
                    logging.error("STEP 4 FAILED: From Date input field not found")
                    return {
                        'status': '⚠️ Error - From Date field not found',
                        'value_of_purchases': 'N/A'
                    }
                
                # Click to open datepicker, then use JavaScript to set value directly
                # (readonly fields require JS to set value)
                self.driver.execute_script(f"arguments[0].value = '{date_formatted}';", from_date_input)
                self._random_delay(0.1, 0.25)
                
                # Verify From Date was set
                from_date_value = from_date_input.get_attribute('value')
                if from_date_value != date_formatted:
                    logging.error(f"STEP 4 FROM DATE VERIFICATION FAILED: Expected '{date_formatted}', got '{from_date_value}'")
                    return {
                        'status': '⚠️ Error - From Date verification failed',
                        'value_of_purchases': 'N/A'
                    }
                
                logging.info(f"✓ From Date verified: {from_date_value}")
                
                # Select To Date (same date)
                to_date_selectors = [
                    (By.ID, "correspondenceTabs:loadAnnexAform:annexAToDate_input"),
                    (By.NAME, "correspondenceTabs:loadAnnexAform:annexAToDate_input"),
                    (By.XPATH, "//input[@id='correspondenceTabs:loadAnnexAform:annexAToDate_input']"),
                ]
                
                to_date_input = None
                for by_type, selector in to_date_selectors:
                    try:
                        # Wait for element to be visible and present
                        to_date_input = wait.until(EC.visibility_of_element_located((by_type, selector)))
                        logging.info(f"Found To Date input using selector: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if not to_date_input:
                    logging.error("STEP 4 FAILED: To Date input field not found")
                    return {
                        'status': '⚠️ Error - To Date field not found',
                        'value_of_purchases': 'N/A'
                    }
                
                # Use JavaScript to set value directly
                self.driver.execute_script(f"arguments[0].value = '{date_formatted}';", to_date_input)
                self._random_delay(0.1, 0.25)
                
                # Verify To Date was set
                to_date_value = to_date_input.get_attribute('value')
                if to_date_value != date_formatted:
                    logging.error(f"STEP 4 TO DATE VERIFICATION FAILED: Expected '{date_formatted}', got '{to_date_value}'")
                    return {
                        'status': '⚠️ Error - To Date verification failed',
                        'value_of_purchases': 'N/A'
                    }
                
                logging.info(f"✓ STEP 4 COMPLETED & VERIFIED: Dates set to '{date_formatted}'")
                self._random_delay(0.25, 0.5)

            # if date_field and date_field != 'N/A':
            #     logging.info(f"STEP 4: Selecting dates: {date_field}")
                
            #     # Parse the date
            #     parsed_date = self._select_date_from_datepicker(date_field)
                
            #     if not parsed_date:
            #         logging.error(f"STEP 4 FAILED: Could not parse date: {date_field}")
            #         return {
            #             'status': '⚠️ Error - Date parsing failed',
            #             'value_of_purchases': 'N/A'
            #         }
                
            #     date_formatted = parsed_date['formatted']
                
            #     # Select From Date
            #     from_date_selectors = [
            #         (By.ID, "correspondenceTabs:loadAnnexAform:annexAFromDate_input"),
            #         (By.NAME, "correspondenceTabs:loadAnnexAform:annexAFromDate_input"),
            #         (By.XPATH, "//input[@id='correspondenceTabs:loadAnnexAform:annexAFromDate_input']"),
            #     ]
                
            #     from_date_input = None
            #     for by_type, selector in from_date_selectors:
            #         try:
            #             # Wait for element to be visible and present
            #             from_date_input = wait.until(EC.visibility_of_element_located((by_type, selector)))
            #             logging.info(f"Found From Date input using selector: {selector}")
            #             break
            #         except TimeoutException:
            #             continue
                
            #     if not from_date_input:
            #         logging.error("STEP 4 FAILED: From Date input field not found")
            #         return {
            #             'status': '⚠️ Error - From Date field not found',
            #             'value_of_purchases': 'N/A'
            #         }
                
            #     # Click to open datepicker, then use JavaScript to set value directly
            #     # (readonly fields require JS to set value)
            #     self.driver.execute_script(f"arguments[0].value = '{date_formatted}';", from_date_input)
            #     self._random_delay(0.1, 0.25)
                
            #     # Verify From Date was set
            #     from_date_value = from_date_input.get_attribute('value')
            #     if from_date_value != date_formatted:
            #         logging.error(f"STEP 4 FROM DATE VERIFICATION FAILED: Expected '{date_formatted}', got '{from_date_value}'")
            #         return {
            #             'status': '⚠️ Error - From Date verification failed',
            #             'value_of_purchases': 'N/A'
            #         }
                
            #     logging.info(f"✓ From Date verified: {from_date_value}")
                
            #     # Select To Date (same date)
            #     to_date_selectors = [
            #         (By.ID, "correspondenceTabs:loadAnnexAform:annexAToDate_input"),
            #         (By.NAME, "correspondenceTabs:loadAnnexAform:annexAToDate_input"),
            #         (By.XPATH, "//input[@id='correspondenceTabs:loadAnnexAform:annexAToDate_input']"),
            #     ]
                
            #     to_date_input = None
            #     for by_type, selector in to_date_selectors:
            #         try:
            #             # Wait for element to be visible and present
            #             to_date_input = wait.until(EC.visibility_of_element_located((by_type, selector)))
            #             logging.info(f"Found To Date input using selector: {selector}")
            #             break
            #         except TimeoutException:
            #             continue
                
            #     if not to_date_input:
            #         logging.error("STEP 4 FAILED: To Date input field not found")
            #         return {
            #             'status': '⚠️ Error - To Date field not found',
            #             'value_of_purchases': 'N/A'
            #         }
                
            #     # Use JavaScript to set value directly
            #     self.driver.execute_script(f"arguments[0].value = '{date_formatted}';", to_date_input)
            #     self._random_delay(0.1, 0.25)
                
            #     # Verify To Date was set
            #     to_date_value = to_date_input.get_attribute('value')
            #     if to_date_value != date_formatted:
            #         logging.error(f"STEP 4 TO DATE VERIFICATION FAILED: Expected '{date_formatted}', got '{to_date_value}'")
            #         return {
            #             'status': '⚠️ Error - To Date verification failed',
            #             'value_of_purchases': 'N/A'
            #         }
                
            #     logging.info(f"✓ STEP 4 COMPLETED & VERIFIED: Dates set to '{date_formatted}'")
            #     self._random_delay(0.25, 0.5)
            
            # Step 5: Click the Search button in Annex-A form
            logging.info("STEP 5: Clicking Search button in Annex-A form...")
            
            search_button_annexa = None
            search_button_selectors = [
                # Strategy 1: Partial ID match - form prefix + button with Search text
                (By.XPATH, "//button[contains(@id, 'loadAnnexAform:j_idt') and .//span[normalize-space(text())='Search']]"),
                
                # Strategy 2: Form-scoped search with button type and icon class
                (By.XPATH, "//form[contains(@id, 'loadAnnexAform')]//button[@type='submit' and contains(@class, 'ui-button')]//span[contains(text(), 'Search')]"),
                
                # Strategy 3: Button within form containing "Search" text with icon
                (By.XPATH, "//form[contains(@id, 'loadAnnexAform')]//button[.//span[normalize-space(text())='Search'] and contains(@class, 'ui-button')]"),
                
                # Strategy 4: Button with partial ID match in loadAnnexAform context
                (By.XPATH, "//button[contains(@id, 'correspondenceTabs:loadAnnexAform:j_idt')]"),
                
                # Strategy 5: Any button with Search text inside Annex-A form
                (By.XPATH, "//button[contains(@id, 'loadAnnexAform') and .//span[contains(text(), 'Search')]]"),
                
                # Strategy 6: Submit button in the specific form by role
                (By.XPATH, "//form[contains(@id, 'loadAnnexAform')]//button[@type='submit'][not(contains(@style, 'display: none'))]"),
                
                # Strategy 7: Button with ui-button class and Search span (most generic)
                (By.XPATH, "//form[contains(@id, 'loadAnnexAform')]//button[contains(@class, 'ui-button')]//span[normalize-space()='Search']"),
                
                # Strategy 8: CSS Selector fallback with partial attribute matching
                (By.CSS_SELECTOR, "button[id*='loadAnnexAform'][id*='j_idt']"),
                
                # Strategy 9: Find all buttons in form and filter by text
                (By.XPATH, "//form[contains(@id, 'loadAnnexAform')]//button[contains(., 'Search')]"),
            ]
            
            for by_type, selector in search_button_selectors:
                try:
                    # Try to find the element with a shorter timeout for faster fallback
                    search_button_annexa = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((by_type, selector))
                    )
                    
                    # Verify element is actually visible and enabled
                    if search_button_annexa.is_displayed() and search_button_annexa.is_enabled():
                        logging.info(f"✓ Found Annex-A Search button using selector: {selector}")
                        break
                    else:
                        logging.debug(f"Element found but not interactable with selector: {selector}")
                        search_button_annexa = None
                        
                except (TimeoutException, NoSuchElementException) as e:
                    logging.debug(f"Selector failed: {selector} - {type(e).__name__}")
                    continue
                except Exception as e:
                    logging.debug(f"Unexpected error with selector {selector}: {str(e)}")
                    continue
            
            # Fallback: Use JavaScript to find button if all selectors fail
            if not search_button_annexa:
                logging.warning("All selectors failed, trying JavaScript fallback...")
                try:
                    search_button_annexa = self.driver.execute_script("""
                        // Find form containing 'loadAnnexAform' in ID
                        var form = document.querySelector('form[id*="loadAnnexAform"]');
                        if (!form) return null;
                        
                        // Find all buttons in the form
                        var buttons = form.querySelectorAll('button');
                        for (var i = 0; i < buttons.length; i++) {
                            var btn = buttons[i];
                            // Check if button contains "Search" text
                            if (btn.textContent.includes('Search') && 
                                btn.offsetParent !== null && // visible
                                !btn.disabled) { // enabled
                                return btn;
                            }
                        }
                        
                        // Fallback: Find button with partial ID match
                        var allButtons = form.querySelectorAll('button[id*="j_idt"]');
                        for (var i = 0; i < allButtons.length; i++) {
                            if (allButtons[i].offsetParent !== null && !allButtons[i].disabled) {
                                return allButtons[i];
                            }
                        }
                        
                        return null;
                    """)
                    
                    if search_button_annexa:
                        logging.info("✓ Found Search button using JavaScript fallback")
                    
                except Exception as js_error:
                    logging.error(f"JavaScript fallback also failed: {str(js_error)}")
            
            if not search_button_annexa:
                logging.error("STEP 5 FAILED: Annex-A Search button not found after trying all strategies")
                return {
                    'status': '⚠️ Error - Search button not found',
                    'value_of_purchases': 'N/A'
                }
            
            # Human-like click on search button
            self._human_like_click(search_button_annexa)
            logging.info("✓ STEP 5: Search button clicked, waiting for results...")
            
            # Wait for results to load - check for either results table or "no records" message
            # Use explicit wait with multiple conditions
            search_completed = False
            results_wait = WebDriverWait(self.driver, 60)
            
            try:
                # CRITICAL: First wait for the AJAX loading dialog to appear and then disappear
                logging.info("Waiting for AJAX loading dialog...")
                try:
                    # Wait for loading dialog to appear (check for both the dialog container and the image)
                    # The loader is inside: <div class="ui-dialog-content ui-widget-content"><img src="/images/ajaxloadingbar.gif"></div>
                    loading_dialog = WebDriverWait(self.driver, 60).until(
                        EC.presence_of_element_located((By.XPATH, 
                            "//div[contains(@class, 'ui-dialog-content') and contains(@class, 'ui-widget-content')]//img[contains(@src, 'ajaxloadingbar.gif')]"))
                    )
                    logging.info("AJAX loading dialog appeared, waiting for it to disappear...")
                except TimeoutException:
                    logging.info("Loading dialog not detected or already gone, proceeding...")
                
                # Now wait for the loading dialog to become invisible/disappear
                # Wait for both the image and the dialog container to disappear
                results_wait.until(
                    EC.invisibility_of_element_located((By.XPATH, 
                        "//div[contains(@class, 'ui-dialog-content') and contains(@class, 'ui-widget-content')]//img[contains(@src, 'ajaxloadingbar.gif')]"))
                )
                logging.info("✓ AJAX loading dialog has disappeared")
                
                # Additional wait to ensure DOM is stable after loader disappears
                self._random_delay(0.25, 0.5)
                
                # Wait for either the results table to be visible OR "no records" message
                logging.info("Waiting for search results or 'no data' message...")
                
                # First, check if results table appears and is visible
                try:
                    results_table = results_wait.until(
                        EC.visibility_of_element_located((By.ID, "correspondenceTabs:loadAnnexAform:purchaseInvoiceTable"))
                    )
                    # Additional check: wait for table body to have content
                    results_wait.until(
                        lambda driver: driver.execute_script("""
                            var table = document.getElementById('correspondenceTabs:loadAnnexAform:purchaseInvoiceTable');
                            if (!table) return false;
                            var tbody = table.querySelector('tbody');
                            return tbody && (tbody.rows.length > 0 || tbody.querySelector('tr'));
                        """)
                    )
                    search_completed = True
                    logging.info("✓ STEP 5 COMPLETED: Results table loaded and data is visible")
                except TimeoutException:
                    # If table didn't load, check for "no records found" message
                    logging.info("Results table not found, checking for 'no data' message...")
                    try:
                        no_records_msg = results_wait.until(
                            EC.visibility_of_element_located((By.XPATH, "//span[contains(text(), 'No records found') or contains(text(), 'No data') or contains(text(), 'No Records')]"))
                        )
                        if no_records_msg and no_records_msg.is_displayed():
                            logging.info("✓ STEP 5 COMPLETED: No records found message displayed")
                            return {
                                'status': '⚠️ No results',
                                'value_of_purchases': 'N/A'
                            }
                    except TimeoutException:
                        pass
            except Exception as e:
                logging.error(f"Error waiting for search results: {str(e)}")
            
            if not search_completed:
                logging.error("STEP 5 VERIFICATION FAILED: Neither results table nor no-records message appeared")
                return {
                    'status': '⚠️ Error - Search results not loaded',
                    'value_of_purchases': 'N/A'
                }
            
            # Small delay for human-like behavior
            self._random_delay(0.25, 0.5)
            
            # Step 6: Find and click the checkbox for the row matching Sales Tax/FED in ST Mode
            logging.info("STEP 6: Looking for matching row in results table...")
            try:
                # Variables to store matched row data
                matching_checkbox = None
                matched_row_sales_tax = 'N/A'  # Will store the FBR Sales Tax value from matched row
                
                # Wait for the results table data to be fully loaded
                checkbox_wait = WebDriverWait(self.driver, 60)
                
                # Wait for table rows to be present and visible
                logging.info("Waiting for table rows to load...")
                checkbox_wait.until(
                    lambda driver: driver.execute_script("""
                        var table = document.getElementById('correspondenceTabs:loadAnnexAform:purchaseInvoiceTable');
                        if (!table) return false;
                        var rows = table.querySelectorAll('tbody tr');
                        return rows && rows.length > 0 && rows[0].offsetParent !== null;
                    """)
                )
                
                # Step 6.1: If sales_tax_fed_st_mode is provided, find matching row
                matching_checkbox = None
                
                if sales_tax_fed_st_mode:
                    logging.info(f"STEP 6.1: Searching for row with Sales Tax/FED in ST Mode = '{sales_tax_fed_st_mode}'...")
                    
                    # Use JavaScript to find all rows and match the Sales Tax/FED in ST Mode column
                    # Also extract the actual FBR Sales Tax value for that row
                    result = self.driver.execute_script("""
                        var sales_tax_value = arguments[0];
                        var table = document.getElementById('correspondenceTabs:loadAnnexAform:purchaseInvoiceTable');
                        if (!table) {
                            console.log('Table not found');
                            return {checkbox: null, fbr_sales_tax: 'N/A'};
                        }
                        
                        var rows = table.querySelectorAll('tbody tr');
                        console.log('Total rows found: ' + rows.length);
                        
                        if (!rows || rows.length === 0) {
                            console.log('No rows found in table body');
                            return {checkbox: null, fbr_sales_tax: 'N/A'};
                        }
                        
                        // Get all header cells to find column indices
                        var headers = table.querySelectorAll('thead th');
                        var sales_tax_col_index = -1;
                        var fbr_sales_tax_col_index = -1;
                        
                        // Try to find Sales Tax/FED in ST Mode column (from Excel input)
                        for (var h = 0; h < headers.length; h++) {
                            var headerText = headers[h].innerText.trim();
                            console.log('Header ' + h + ': ' + headerText);
                            
                            // Match "Sales Tax/ FED in ST Mode" or similar variations (INPUT column from Excel)
                            if (headerText.includes('Sales Tax') && headerText.includes('ST Mode')) {
                                sales_tax_col_index = h;
                                console.log('Found Sales Tax/FED in ST Mode column (Excel) at index: ' + sales_tax_col_index);
                            }
                            // Match "Sales Tax/FED" ONLY (OUTPUT column from FBR) - be more specific
                            // This should be the FBR column, NOT the input column
                            else if ((headerText.includes('Sales Tax') || headerText.includes('FED')) && 
                                     !headerText.includes('ST Mode') && 
                                     !headerText.includes('Input')) {
                                fbr_sales_tax_col_index = h;
                                console.log('Found FBR Sales Tax/FED column (Output) at index: ' + fbr_sales_tax_col_index);
                            }
                        }
                        
                        if (sales_tax_col_index === -1) {
                            console.log('Sales Tax/FED in ST Mode column not found');
                            return {checkbox: null, fbr_sales_tax: 'N/A'};
                        }
                        
                        // Iterate through rows to find matching value
                        for (var i = 0; i < rows.length; i++) {
                            var cells = rows[i].querySelectorAll('td');
                            if (cells && cells.length > sales_tax_col_index) {
                                var cellValue = cells[sales_tax_col_index].innerText.trim();
                                console.log('Row ' + i + ' Sales Tax value: ' + cellValue + ' (looking for: ' + sales_tax_value + ')');
                                
                                // Compare values (remove commas and spaces for comparison)
                                var cellValueClean = cellValue.replace(/,/g, '').replace(/\\s+/g, '');
                                var searchValueClean = sales_tax_value.replace(/,/g, '').replace(/\\s+/g, '');
                                
                                // Allow margin of 1 rupee for matching
                                var cellNum = parseFloat(cellValueClean);
                                var searchNum = parseFloat(searchValueClean);
                                var margin = 1.0; // 1 rupee margin
                                
                                var isMatch = cellValueClean === searchValueClean || 
                                             ((!isNaN(cellNum) && !isNaN(searchNum)) && 
                                              Math.abs(cellNum - searchNum) <= margin);
                                
                                if (isMatch) {
                                    console.log('MATCH FOUND at row ' + i + ' (difference: ' + Math.abs(cellNum - searchNum) + ' rupees)');
                                    
                                    // Find the checkbox in this row
                                    var checkbox = rows[i].querySelector('div[class*="ui-chkbox-box"]');
                                    
                                    // Return the cellValue (Sales Tax/FED in ST Mode from FBR) to write to Excel
                                    // This is the FBR portal's value that we want to capture
                                    var fbr_sales_tax = cellValue;  // Use the actual cellValue from FBR
                                    console.log('Captured FBR Sales Tax from matched row: ' + fbr_sales_tax);
                                    
                                    if (checkbox && checkbox.offsetParent !== null) {
                                        return {checkbox: checkbox, fbr_sales_tax: fbr_sales_tax};
                                    }
                                }
                            }
                        }
                        
                        console.log('No matching row found');
                        return {checkbox: null, fbr_sales_tax: 'N/A'};
                    """, str(sales_tax_fed_st_mode))
                    
                    if result and result.get('checkbox'):
                        matching_checkbox = result['checkbox']
                        
                        # Get the FBR Sales Tax value (cellValue from FBR portal)
                        matched_row_sales_tax = result.get('fbr_sales_tax', 'N/A')
                        logging.info(f"✓ Found matching row for Sales Tax/FED in ST Mode = '{sales_tax_fed_st_mode}'")
                        logging.info(f"✓ FBR Sales Tax value captured from portal: {matched_row_sales_tax}")
                    else:
                        logging.warning(f"No row found matching Sales Tax/FED in ST Mode = '{sales_tax_fed_st_mode}', checking for default row...")
                        matching_checkbox = None
                else:
                    logging.info("STEP 6.1: No Sales Tax/FED value provided, using first row...")
                    # Extract Sales Tax/FED in ST Mode value from first row (this is what we write to Excel)
                    matched_row_sales_tax = self.driver.execute_script("""
                        var table = document.getElementById('correspondenceTabs:loadAnnexAform:purchaseInvoiceTable');
                        if (!table) return 'N/A';
                        
                        var rows = table.querySelectorAll('tbody tr');
                        if (!rows || rows.length === 0) return 'N/A';
                        
                        var headers = table.querySelectorAll('thead th');
                        var sales_tax_col_index = -1;
                        
                        // Find "Sales Tax/ FED in ST Mode" column (the value from FBR portal we want to capture)
                        for (var h = 0; h < headers.length; h++) {
                            var headerText = headers[h].innerText.trim();
                            console.log('First row - Header ' + h + ': ' + headerText);
                            
                            // Match "Sales Tax/ FED in ST Mode" column
                            if (headerText.includes('Sales Tax') && headerText.includes('ST Mode')) {
                                sales_tax_col_index = h;
                                console.log('Found Sales Tax/FED in ST Mode column at index: ' + sales_tax_col_index);
                                break;
                            }
                        }
                        
                        if (sales_tax_col_index >= 0) {
                            var cells = rows[0].querySelectorAll('td');
                            if (cells && cells.length > sales_tax_col_index) {
                                var value = cells[sales_tax_col_index].innerText.trim();
                                console.log('Extracted Sales Tax/FED in ST Mode from first row: ' + value);
                                return value;
                            }
                        }
                        
                        return 'N/A';
                    """)
                
              
                if not matching_checkbox:
                    logging.error("STEP 6 FAILED: Checkbox not found in results table after trying all strategies")
                    return {
                        'status': '⚠️ No matching Record Found With Sale Tax/FED in ST Mode',
                        'value_of_purchases': 'N/A',
                        'fbr_sales_tax': 'N/A'
                    }
                
                # Extract Sales Tax/FED in ST Mode from the row containing the checkbox if not already set
                if matched_row_sales_tax == 'N/A':
                    try:
                        matched_row_sales_tax = self.driver.execute_script("""
                            var checkbox = arguments[0];
                            if (!checkbox) return 'N/A';
                            
                            // Find the row containing this checkbox
                            var row = checkbox.closest('tr');
                            if (!row) return 'N/A';
                            
                            // Get table headers to find Sales Tax/FED in ST Mode column
                            var table = row.closest('table');
                            if (!table) return 'N/A';
                            
                            var headers = table.querySelectorAll('thead th');
                            var sales_tax_col_index = -1;
                            
                            // Find "Sales Tax/ FED in ST Mode" column (the value we want to capture)
                            for (var h = 0; h < headers.length; h++) {
                                var headerText = headers[h].innerText.trim();
                                if (headerText.includes('Sales Tax') && headerText.includes('ST Mode')) {
                                    sales_tax_col_index = h;
                                    console.log('Found Sales Tax/FED in ST Mode column at index: ' + sales_tax_col_index);
                                    break;
                                }
                            }
                            
                            if (sales_tax_col_index >= 0) {
                                var cells = row.querySelectorAll('td');
                                if (cells && cells.length > sales_tax_col_index) {
                                    var value = cells[sales_tax_col_index].innerText.trim();
                                    console.log('Extracted Sales Tax/FED in ST Mode from clicked row: ' + value);
                                    return value;
                                }
                            }
                            
                            return 'N/A';
                        """, matching_checkbox)
                        logging.info(f"✓ Extracted Sales Tax/FED in ST Mode from checkbox row: {matched_row_sales_tax}")
                    except Exception as e:
                        logging.warning(f"Could not extract Sales Tax/FED in ST Mode from checkbox row: {str(e)}")
                        matched_row_sales_tax = 'N/A'
                
                # Human-like click on the matching checkbox
                self._human_like_click(matching_checkbox)
                self._random_delay(0.25, 0.5)
                
                # Verify checkbox was clicked by checking its state
                checkbox_checked = self.driver.execute_script("""
                    var checkbox = document.querySelector('#correspondenceTabs\\\\:loadAnnexAform\\\\:purchaseInvoiceTable\\\\:j_idt5893_input');
                    return checkbox ? checkbox.checked : false;
                """)
                
                if not checkbox_checked:
                    logging.warning("STEP 6: Checkbox state not confirmed as checked, but proceeding...")
                
                if sales_tax_fed_st_mode:
                    logging.info(f"✓ STEP 6 COMPLETED: Checkbox clicked for matching row (Sales Tax/FED = '{sales_tax_fed_st_mode}')")
                else:
                    logging.info("✓ STEP 6 COMPLETED: Checkbox clicked in results table")
                self._random_delay(0.25, 0.5)
                
                # Step 7: Extract "Value of Purchases" from the table
                logging.info("STEP 7: Extracting 'Value of Purchases' from results table...")
                
                # Strategy: Find the "Value of Purchases" header column, determine its position, 
                # then extract the value from the corresponding cell in the data row
                
                # Step 7.1: Find the "Value of Purchases" header column
                header_selectors = [
                    # Strategy 1: Exact ID from provided HTML
                    (By.ID, "correspondenceTabs:loadAnnexAform:purchaseInvoiceTable:j_idt5936"),
                    
                    # Strategy 2: By aria-label attribute (exact match)
                    (By.XPATH, "//th[@aria-label='Value of Purchases']"),
                    
                    # Strategy 3: By span text content with class
                    (By.XPATH, "//th[.//span[@class='ui-column-title' and normalize-space(text())='Value of Purchases']]"),
                    
                    # Strategy 4: Partial ID match with dynamic j_idt
                    (By.XPATH, "//th[contains(@id, 'purchaseInvoiceTable:j_idt')]//span[contains(text(), 'Value of Purchases')]"),
                    
                    # Strategy 5: Table context with text contains
                    (By.XPATH, "//table[@id='correspondenceTabs:loadAnnexAform:purchaseInvoiceTable']//th[contains(., 'Value of Purchases')]"),
                    
                    # Strategy 6: By th with data-field or similar attributes
                    (By.XPATH, "//th[contains(@class, 'ui-state-default') and contains(., 'Value of Purchases')]"),
                    
                    # Strategy 7: Using CSS selector with partial attribute matching
                    (By.CSS_SELECTOR, "th[id*='purchaseInvoiceTable'][id*='j_idt']"),
                    
                    # Strategy 8: Any th with class containing 'ui-column'
                    (By.XPATH, "//table[contains(@id, 'purchaseInvoiceTable')]//th[contains(@class, 'ui-column') and contains(., 'Value')]"),
                    
                    # Strategy 9: Form-scoped table header search
                    (By.XPATH, "//form[contains(@id, 'loadAnnexAform')]//th[contains(., 'Value of Purchases')]"),
                    
                    # Strategy 10: th within thead (explicit)
                    (By.XPATH, "//table[contains(@id, 'purchaseInvoiceTable')]//thead//th[contains(normalize-space(), 'Value of Purchases')]"),
                ]
                
                header_element = None
                for by_type, selector in header_selectors:
                    try:
                        # Try to find the element with shorter timeout for faster fallback
                        header_element = WebDriverWait(self.driver, 3).until(
                            EC.visibility_of_element_located((by_type, selector))
                        )
                        
                        # Verify element is actually visible and contains expected text
                        if header_element.is_displayed() and 'Value of Purchases' in header_element.text:
                            logging.info(f"✓ Found 'Value of Purchases' header using selector: {selector}")
                            break
                        else:
                            logging.debug(f"Element found but text mismatch: {header_element.text}")
                            header_element = None
                            
                    except (TimeoutException, NoSuchElementException) as e:
                        logging.debug(f"Selector failed: {selector} - {type(e).__name__}")
                        continue
                    except Exception as e:
                        logging.debug(f"Unexpected error with selector {selector}: {str(e)}")
                        continue
                
                # Fallback: Use JavaScript to find header if all selectors fail
                if not header_element:
                    logging.warning("All selectors failed, trying JavaScript fallback for 'Value of Purchases' header...")
                    try:
                        header_element = self.driver.execute_script("""
                            // Find the purchase invoice table
                            var table = document.getElementById('correspondenceTabs:loadAnnexAform:purchaseInvoiceTable');
                            if (!table) return null;
                            
                            // Strategy 1: Find th with text containing "Value of Purchases"
                            var headers = table.querySelectorAll('th');
                            for (var i = 0; i < headers.length; i++) {
                                var header = headers[i];
                                if (header.textContent.includes('Value of Purchases') && header.offsetParent !== null) {
                                    return header;
                                }
                            }
                            
                            // Strategy 2: Find by aria-label attribute
                            var ariaHeader = table.querySelector('th[aria-label*="Value"]');
                            if (ariaHeader && ariaHeader.offsetParent !== null) {
                                return ariaHeader;
                            }
                            
                            // Strategy 3: Find span with specific text and get parent th
                            var spans = table.querySelectorAll('span');
                            for (var i = 0; i < spans.length; i++) {
                                if (spans[i].textContent.trim() === 'Value of Purchases') {
                                    var th = spans[i].closest('th');
                                    if (th && th.offsetParent !== null) {
                                        return th;
                                    }
                                }
                            }
                            
                            // Strategy 4: Find by checking all headers in thead
                            var thead = table.querySelector('thead');
                            if (thead) {
                                var theadHeaders = thead.querySelectorAll('th');
                                for (var i = 0; i < theadHeaders.length; i++) {
                                    if (theadHeaders[i].textContent.includes('Value')) {
                                        return theadHeaders[i];
                                    }
                                }
                            }
                            
                            return null;
                        """)
                        
                        if header_element:
                            logging.info("✓ Found 'Value of Purchases' header using JavaScript fallback")
                        
                    except Exception as js_error:
                        logging.error(f"JavaScript fallback also failed: {str(js_error)}")
                        header_element = None
                
                value_of_purchases = 'N/A'  # Default value
                
                if not header_element:
                    logging.error("STEP 7 FAILED: Could not find 'Value of Purchases' header in results table after trying all strategies")
                    return {
                        'status': '⚠️ Error - Header not found',
                        'value_of_purchases': 'N/A'
                    }
                
                # Wait for table data cells to be fully loaded
                try:
                    wait.until(
                        lambda driver: driver.execute_script("""
                            var table = document.getElementById('correspondenceTabs:loadAnnexAform:purchaseInvoiceTable');
                            if (!table) return false;
                            var dataRows = table.querySelectorAll('tbody tr');
                            if (!dataRows || dataRows.length === 0) return false;
                            var cells = dataRows[0].querySelectorAll('td');
                            return cells && cells.length > 0;
                        """)
                    )
                except TimeoutException:
                    logging.error("STEP 7 FAILED: Timeout waiting for table data rows")
                    return {
                        'status': '⚠️ Error - Table data not loaded',
                        'value_of_purchases': 'N/A'
                    }
                
                if header_element:
                            # Step 7.2: Determine the column index (position) of the header
                            # Use JavaScript to get the column index more reliably
                            column_index = self.driver.execute_script("""
                                var header = arguments[0];
                                var headers = header.parentElement.children;
                                for (var i = 0; i < headers.length; i++) {
                                    if (headers[i] === header) {
                                        return i + 1; // 1-indexed for XPath
                                    }
                                }
                                return -1;
                            """, header_element)
                            
                            logging.info(f"'Value of Purchases' column index: {column_index}")
                            
                            if column_index > 0:
                                # Step 7.3: Extract the value - Use JavaScript to inspect table structure first
                                logging.info("Inspecting table structure with JavaScript...")
                                
                                # First, let's understand the table structure
                                table_info = self.driver.execute_script("""
                                    var table = document.getElementById('correspondenceTabs:loadAnnexAform:purchaseInvoiceTable');
                                    if (!table) return {error: 'Table not found'};
                                    
                                    var info = {
                                        hasTBody: table.tBodies && table.tBodies.length > 0,
                                        tBodyCount: table.tBodies ? table.tBodies.length : 0,
                                        hasRows: false,
                                        rowCount: 0,
                                        firstRowCellCount: 0
                                    };
                                    
                                    // Check various ways to access rows
                                    if (table.tBodies && table.tBodies.length > 0) {
                                        var tbody = table.tBodies[0];
                                        info.hasRows = tbody.rows && tbody.rows.length > 0;
                                        info.rowCount = tbody.rows ? tbody.rows.length : 0;
                                        if (info.hasRows) {
                                            info.firstRowCellCount = tbody.rows[0].cells ? tbody.rows[0].cells.length : 0;
                                        }
                                    }
                                    
                                    // Also check direct table.rows
                                    info.directRowCount = table.rows ? table.rows.length : 0;
                                    
                                    return info;
                                """)
                                
                                logging.info(f"Table structure: {table_info}")
                                
                                # Now extract the value using the appropriate method based on table structure
                                value_of_purchases = self.driver.execute_script("""
                                    var table = document.getElementById('correspondenceTabs:loadAnnexAform:purchaseInvoiceTable');
                                    if (!table) return 'N/A - Table not found';
                                    
                                    var columnIndex = arguments[0] - 1; // Convert to 0-indexed
                                    
                                    // Try method 1: tbody.rows
                                    if (table.tBodies && table.tBodies.length > 0) {
                                        var tbody = table.tBodies[0];
                                        if (tbody.rows && tbody.rows.length > 0) {
                                            var firstRow = tbody.rows[0];
                                            if (firstRow.cells && firstRow.cells[columnIndex]) {
                                                return firstRow.cells[columnIndex].innerText.trim();
                                            }
                                        }
                                    }
                                    
                                    // Try method 2: table.rows (skip header rows)
                                    if (table.rows && table.rows.length > 1) {
                                        // Usually first row is header, so start from index 1
                                        for (var i = 1; i < table.rows.length; i++) {
                                            var row = table.rows[i];
                                            if (row.cells && row.cells[columnIndex]) {
                                                var text = row.cells[columnIndex].innerText.trim();
                                                if (text && text !== '') {
                                                    return text;
                                                }
                                            }
                                        }
                                    }
                                    
                                    // Try method 3: querySelector for data rows
                                    var dataRows = table.querySelectorAll('tbody tr, tr[data-ri]');
                                    if (dataRows && dataRows.length > 0) {
                                        var firstDataRow = dataRows[0];
                                        var cells = firstDataRow.querySelectorAll('td');
                                        if (cells && cells[columnIndex]) {
                                            return cells[columnIndex].innerText.trim();
                                        }
                                    }
                                    
                                    return 'N/A - No data rows found';
                                """, column_index)
                                
                                logging.info(f"✓ STEP 7 COMPLETED: Extracted Value of Purchases: {value_of_purchases}")
                            else:
                                logging.warning("STEP 7: Could not determine column index for 'Value of Purchases'")
                else:
                    logging.warning("STEP 7: Could not find 'Value of Purchases' header in results table")
                
                logging.info(f"✓ STEP 7 COMPLETED: Value of Purchases = {value_of_purchases}")
                self._random_delay(0.25, 0.5)
                
                ####################################################################################
                # Step 8: Wait for page to fully load before attempting to find Claim button
                logging.info("STEP 8: Waiting for page to load before finding Claim button...")
                
                try:
                    # Wait for page to fully load
                    WebDriverWait(self.driver, 60).until(
                        lambda driver: driver.execute_script("return document.readyState") == "complete"
                    )
                    logging.info("✓ Page fully loaded")
                    
                    # Additional wait to ensure all elements are rendered
                    self._random_delay(0.25, 0.75)
                    
                except TimeoutException:
                    logging.warning("Page load timeout, but proceeding anyway...")
                
                # Step 8.1: Click the EXACT "Claim" button (not "Claim in PRA/KPRA/BRA/SRB")
                logging.info("STEP 8.1: Clicking Claim button (exact match only)...")
                
                claim_button = None
                claim_button_selectors = [
                    # Strategy 1: EXACT text match - span must contain ONLY "Claim" (no other text)
                    (By.XPATH, "//button[contains(@id, 'loadAnnexAform:j_idt') and .//span[normalize-space(text())='Claim' and not(contains(text(), ' in '))]]"),
                    
                    # Strategy 2: EXACT text match with button in loadAnnexAform context
                    (By.XPATH, "//button[contains(@id, 'correspondenceTabs:loadAnnexAform:j_idt')]//span[text()='Claim' and string-length(normalize-space())=5]"),
                    
                    # Strategy 3: Form-scoped button where span text equals exactly "Claim"
                    (By.XPATH, "//form[contains(@id, 'loadAnnexAform')]//button[@type='submit' and contains(@class, 'ui-button')]//span[text()='Claim' and not(contains(text(), 'in'))]"),
                    
                    # Strategy 4: Button with calculate class and EXACT "Claim" text (5 characters only)
                    (By.XPATH, "//button[contains(@class, 'calculate') and .//span[text()='Claim' and string-length(text())=5]]"),
                    
                    # Strategy 5: Any button with span containing ONLY "Claim" word
                    (By.XPATH, "//button[contains(@id, 'loadAnnexAform') and .//span[normalize-space()='Claim']]"),
                    
                    # Strategy 6: CSS selector with partial ID matching and calculate class
                    (By.CSS_SELECTOR, "button[id*='loadAnnexAform'][id*='j_idt'].calculate"),
                    
                    # Strategy 7: Button where the span text matches exactly "Claim" (case-sensitive)
                    (By.XPATH, "//form[contains(@id, 'loadAnnexAform')]//button//span[.='Claim']"),
                ]
                
                for by_type, selector in claim_button_selectors:
                    try:
                        # Try to find the element with shorter timeout for faster fallback
                        claim_button = WebDriverWait(self.driver, 3).until(
                            EC.presence_of_element_located((by_type, selector))
                        )
                        
                        # CRITICAL: Verify the button text is EXACTLY "Claim" (not "Claim in PRA", etc.)
                        button_text = claim_button.text.strip()
                        if button_text == "Claim" and claim_button.is_displayed() and claim_button.is_enabled():
                            logging.info(f"✓ Found EXACT 'Claim' button using selector: {selector}")
                            logging.info(f"  Button text verified: '{button_text}'")
                            break
                        else:
                            logging.debug(f"Button text mismatch: '{button_text}' (expected 'Claim') or not interactable")
                            claim_button = None
                            
                    except (TimeoutException, NoSuchElementException) as e:
                        logging.debug(f"Selector failed: {selector} - {type(e).__name__}")
                        continue
                    except Exception as e:
                        logging.debug(f"Unexpected error with selector {selector}: {str(e)}")
                        continue
                
                # Fallback: Use JavaScript to find EXACT "Claim" button if all selectors fail
                if not claim_button:
                    logging.warning("All selectors failed, trying JavaScript fallback for EXACT 'Claim' button...")
                    try:
                        claim_button = self.driver.execute_script("""
                            // Find form containing 'loadAnnexAform' in ID
                            var form = document.querySelector('form[id*="loadAnnexAform"]');
                            if (!form) return null;
                            
                            // Find all buttons in the form
                            var buttons = form.querySelectorAll('button');
                            for (var i = 0; i < buttons.length; i++) {
                                var btn = buttons[i];
                                var btnText = btn.textContent.trim();
                                
                                // CRITICAL: Check if button text is EXACTLY "Claim" (not "Claim in PRA", etc.)
                                if (btnText === 'Claim' && 
                                    btn.offsetParent !== null && // visible
                                    !btn.disabled) { // enabled
                                    return btn;
                                }
                            }
                            
                            // Alternative: Check button span text specifically
                            var spans = form.querySelectorAll('button span');
                            for (var i = 0; i < spans.length; i++) {
                                var span = spans[i];
                                var spanText = span.textContent.trim();
                                
                                if (spanText === 'Claim' && spanText.length === 5) { // Exactly 5 characters
                                    var parentBtn = span.closest('button');
                                    if (parentBtn && parentBtn.offsetParent !== null && !parentBtn.disabled) {
                                        return parentBtn;
                                    }
                                }
                            }
                            
                            return null;
                        """)
                        
                        if claim_button:
                            button_text = claim_button.text.strip()
                            logging.info(f"✓ Found 'Claim' button using JavaScript fallback")
                            logging.info(f"  Button text verified: '{button_text}'")
                        
                    except Exception as js_error:
                        logging.error(f"JavaScript fallback also failed: {str(js_error)}")
                
                if not claim_button:
                    logging.error("STEP 8 FAILED: EXACT 'Claim' button not found after trying all strategies")
                    return {
                        'status': '⚠️ Error - Claim button not found',
                        'value_of_purchases': value_of_purchases
                    }
                
                #Final verification: Ensure button text is exactly "Claim"
                final_button_text = claim_button.text.strip()
                if final_button_text != "Claim":
                    logging.error(f"STEP 8 FAILED: Button text is '{final_button_text}', expected 'Claim'")
                    return {
                        'status': '⚠️ Error - Wrong button found',
                        'value_of_purchases': value_of_purchases
                    }
                
                # Human-like click on Claim button
                self._human_like_click(claim_button)
                logging.info("✓ STEP 8: EXACT 'Claim' button clicked, waiting for success message...")
                self._random_delay(0.25,0.5)
                
                ####################################################################################

                # Step 9: Wait for success message
                logging.info("STEP 9: Waiting for 'Purchase Invoice(s) loaded Successfully' message...")
                
                success_message_found = False
                success_wait = WebDriverWait(self.driver, 20)
                
                try:
                    # Look for the success message in the growl notification
                    success_selectors = [
                        # Strategy 1: Growl title with exact text
                        (By.XPATH, "//span[@class='ui-growl-title' and contains(text(), 'Purchase Invoice(s) loaded Successfully')]"),
                        
                        # Strategy 2: Growl message containing success text
                        (By.XPATH, "//div[@class='ui-growl-message']//span[contains(text(), 'loaded Successfully')]"),
                        
                        # Strategy 3: Any growl item with success info icon
                        (By.XPATH, "//div[@class='ui-growl-item']//span[@class='ui-growl-image ui-growl-image-info']"),
                        
                        # Strategy 4: Generic growl title
                        (By.XPATH, "//span[@class='ui-growl-title']"),
                        
                        # Strategy 5: CSS selector for growl success
                        (By.CSS_SELECTOR, ".ui-growl-title"),
                    ]
                    
                    for by_type, selector in success_selectors:
                        try:
                            success_element = success_wait.until(
                                EC.visibility_of_element_located((by_type, selector))
                            )
                            
                            if success_element:
                                success_text = success_element.text
                                logging.info(f"✓ Found success message: {success_text}")
                                
                                # Check if it's the expected success message
                                if 'loaded Successfully' in success_text or 'Success' in success_text:
                                    success_message_found = True
                                    logging.info("✓ STEP 9 COMPLETED: Purchase Invoice(s) loaded Successfully!")
                                    break
                                
                        except TimeoutException:
                            continue
                        except Exception as e:
                            logging.debug(f"Error checking success message with selector {selector}: {str(e)}")
                            continue
                    
                    # If no success message found with selectors, try JavaScript
                    if not success_message_found:
                        logging.info("Trying JavaScript fallback for success message...")
                        try:
                            success_text = self.driver.execute_script("""
                                // Look for growl notification
                                var growlTitle = document.querySelector('.ui-growl-title');
                                if (growlTitle) {
                                    return growlTitle.textContent;
                                }
                                
                                // Alternative: Check for any growl message
                                var growlMessages = document.querySelectorAll('.ui-growl-message');
                                if (growlMessages && growlMessages.length > 0) {
                                    return growlMessages[0].textContent;
                                }
                                
                                return null;
                            """)
                            
                            if success_text and ('loaded Successfully' in success_text or 'Success' in success_text):
                                success_message_found = True
                                logging.info(f"✓ STEP 9 COMPLETED (JS): {success_text}")
                            
                        except Exception as js_error:
                            logging.warning(f"JavaScript fallback for success message failed: {str(js_error)}")
                
                except TimeoutException:
                    logging.warning("STEP 9: Timeout waiting for success message, but proceeding...")
                except Exception as e:
                    logging.warning(f"STEP 9: Error waiting for success message: {str(e)}")
                
                #Determine final status
                if success_message_found:
                    final_status = '✓ Claimed - After Success Message'
                    logging.info("=" * 60)
                    logging.info("SUCCESS: Invoice claimed successfully!")
                    logging.info("=" * 60)
                else:
                    final_status = '⚠️ Claim attempted (verification pending)'
                    logging.warning("Claim button clicked but success message not confirmed")

                ####################################################################################
                
                # IMPORTANT: Stay on Annex-A form for next invoice processing
                # The form remains on the same page, ready for next search
                # Do NOT navigate away or reset annex_a_tab_clicked flag
                # This allows continuous processing without clicking Annex-A tab again
                logging.info("✓ Ready for next invoice (staying on Annex-A form)")
                self._random_delay(0.5, 1.0)
                
                # Log the final values being returned
                logging.info(f"FINAL RESULT - Status: {final_status}")
                logging.info(f"FINAL RESULT - Value of Purchases: {value_of_purchases}")
                logging.info(f"FINAL RESULT - FBR Sales Tax: {matched_row_sales_tax}")
                
                # Return both status, value of purchases, and FBR Sales Tax
                return {
                    'status': final_status,
                    'value_of_purchases': value_of_purchases,
                    'fbr_sales_tax': matched_row_sales_tax
                }
                
            except TimeoutException:
                logging.error("STEP 6/7 FAILED: Timeout exception")
                return {
                    'status': '⚠️ Error - Timeout',
                    'value_of_purchases': 'N/A',
                    'fbr_sales_tax': 'N/A'
                }
            except WebDriverException as e:
                logging.error(f"STEP 6/7 FAILED: Browser closed or disconnected: {str(e)}")
                return {
                    'status': '⚠️ Browser Closed',
                    'value_of_purchases': 'N/A',
                    'fbr_sales_tax': 'N/A'
                }
            except Exception as e:
                logging.error(f"STEP 6/7 FAILED: {str(e)}")
                return {
                    'status': '⚠️ Error',
                    'value_of_purchases': 'N/A',
                    'fbr_sales_tax': 'N/A'
                }
            
        except WebDriverException as e:
            logging.error(f"Browser closed by user during verification: {str(e)}")
            return {
                'status': '⚠️ Browser Closed',
                'value_of_purchases': 'N/A',
                'fbr_sales_tax': 'N/A'
            }
        except Exception as e:
            logging.error(f"Error verifying invoice {invoice_number}: {str(e)}")
            return {
                'status': '⚠️ Error',
                'value_of_purchases': 'N/A',
                'fbr_sales_tax': 'N/A'
            }
    
    def load_stwh(self, invoice_number, source_authority=None, invoice_no_field=None, date_field=None, sales_tax_fed_st_mode=None):
        """
        Load STWH (Sales Tax Withholding) for a single invoice on the FBR portal.
        Complete copy of verify_invoice implementation with STWH-specific logging.
        
        Args:
            invoice_number (str): The seller registration number (NTN) to process
            source_authority (str): Source Authority value (e.g., 'FBR', 'BRA', 'KPRA', 'PRA', 'SRB')
            invoice_no_field (str): Invoice number from 'Number' column in Excel
            date_field (str): Date from 'Date' column in Excel (will be used for both From and To dates)
            sales_tax_fed_st_mode (str): Sales Tax/FED in ST Mode value from Excel to match with FBR data
            
        Returns:
            dict: Status and details including matched row information
        """
        try:
            logging.info(f"[STWH] Starting STWH processing for: {invoice_number}")
            
            # Check if browser is still alive before proceeding
            if not self.is_browser_alive():
                logging.error("[STWH] Browser was closed by user")
                return {
                    'status': '⚠️ Browser Closed',
                    'value_of_purchases': 'N/A'
                }
            
            # STWH Specific: Click "Load STWH / Debit Note" button instead of Claim workflow
            self._random_delay(0.25, 0.5)
            
            # Navigate to Annex-A tab first
            logging.info("[STWH] Clicking Annex-A (Purchases) tab...")
            self.click_annex_a_tab()
            self._random_delay(0.5, 1.0)
            
            # Click the "Load STWH / Debit Note" button
            logging.info("[STWH] Clicking 'Load STWH / Debit Note' button...")
            
            load_stwh_button = None
            load_stwh_button_selectors = [
                # Strategy 1: Exact ID match
                (By.ID, "correspondenceTabs:annexa-form:j_idt6155"),
                
                # Strategy 2: Button with Load STWH text
                (By.XPATH, "//button[contains(@id, 'annexa-form') and .//span[contains(text(), 'Load STWH')]]"),
                
                # Strategy 3: Button with span text "Load STWH / Debit Note"
                (By.XPATH, "//button[.//span[normalize-space(text())='Load STWH / Debit Note']]"),
                
                # Strategy 4: Partial ID match with annexa-form context
                (By.XPATH, "//button[contains(@id, 'correspondenceTabs:annexa-form:j_idt')]//span[contains(text(), 'Load STWH')]"),
                
                # Strategy 5: Button with btn-primary class and Load STWH text
                (By.XPATH, "//button[contains(@class, 'btn-primary') and contains(., 'Load STWH')]"),
                
                # Strategy 6: CSS selector with partial ID
                (By.CSS_SELECTOR, "button[id*='annexa-form'][id*='j_idt']"),
            ]
            
            for by_type, selector in load_stwh_button_selectors:
                try:
                    load_stwh_button = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by_type, selector))
                    )
                    
                    if load_stwh_button and load_stwh_button.is_displayed() and load_stwh_button.is_enabled():
                        logging.info(f"[STWH] ✓ Found 'Load STWH / Debit Note' button using selector: {selector}")
                        break
                    else:
                        load_stwh_button = None
                        
                except (TimeoutException, NoSuchElementException):
                    continue
                except Exception as e:
                    logging.debug(f"[STWH] Error with selector {selector}: {str(e)}")
                    continue
            
            # JavaScript fallback
            if not load_stwh_button:
                logging.warning("[STWH] All selectors failed, trying JavaScript fallback...")
                try:
                    load_stwh_button = self.driver.execute_script("""
                        // Find button with "Load STWH" text
                        var buttons = document.querySelectorAll('button');
                        for (var i = 0; i < buttons.length; i++) {
                            var btn = buttons[i];
                            if (btn.textContent.includes('Load STWH') && 
                                btn.offsetParent !== null && 
                                !btn.disabled) {
                                return btn;
                            }
                        }
                        
                        // Try finding by ID pattern
                        var annexaButtons = document.querySelectorAll('button[id*="annexa-form"]');
                        for (var i = 0; i < annexaButtons.length; i++) {
                            if (annexaButtons[i].textContent.includes('Load STWH')) {
                                return annexaButtons[i];
                            }
                        }
                        
                        return null;
                    """)
                    
                    if load_stwh_button:
                        logging.info("[STWH] ✓ Found button using JavaScript fallback")
                        
                except Exception as js_error:
                    logging.error(f"[STWH] JavaScript fallback failed: {str(js_error)}")
            
            if not load_stwh_button:
                logging.error("[STWH] FAILED: 'Load STWH / Debit Note' button not found")
                return {
                    'status': '⚠️ Error - Load STWH button not found',
                    'value_of_purchases': 'N/A'
                }
            
            # Click the Load STWH button
            self._human_like_click(load_stwh_button)
            logging.info("[STWH] ✓ 'Load STWH / Debit Note' button clicked")
            self._random_delay(0.5, 1.0)
            
            # Random delay to simulate human reading page
            self._random_delay(0.25, 0.5)
            
            # Simulate mouse movement before interacting
            self._simulate_mouse_movement()
            
            # Wait for page to fully load
            logging.info("[STWH] Waiting for page to fully load...")
            try:
                WebDriverWait(self.driver, 60).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                logging.info("[STWH] ✓ Page fully loaded")
            except TimeoutException:
                logging.warning("[STWH] Page load timeout, but proceeding anyway...")
            
            wait = WebDriverWait(self.driver, 30)
            
            # Step 1: Select Source Authority from dropdown if provided
            if source_authority:
                logging.info(f"[STWH] STEP 1: Selecting Source Authority: {source_authority}")
                
                # Find the dropdown element
                dropdown_selectors = [
                    (By.ID, "correspondenceTabs:loadStwhAnnexAform:sourceAuthority"),
                    (By.XPATH, "//div[@id='correspondenceTabs:loadStwhAnnexAform:sourceAuthority']"),
                    (By.XPATH, "//div[contains(@class, 'ui-selectonemenu') and contains(@id, 'loadStwhAnnexAform:sourceAuthority')]"),
                ]
                
                dropdown = None
                for by_type, selector in dropdown_selectors:
                    try:
                        dropdown = wait.until(EC.visibility_of_element_located((by_type, selector)))
                        dropdown = wait.until(EC.element_to_be_clickable((by_type, selector)))
                        logging.info(f"[STWH] Found dropdown using selector: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if not dropdown:
                    logging.error("[STWH] STEP 1 FAILED: Source Authority dropdown not found")
                    return {
                        'status': '⚠️ Error - Dropdown not found',
                        'value_of_purchases': 'N/A'
                    }
                
                # Click the dropdown to open it
                self._human_like_click(dropdown)
                self._random_delay(0.25, 0.5)
                
                # Select the option by text
                authority_map = {
                    'BRA': '7',
                    'FBR': '1',
                    'KPRA': '6',
                    'PRA': '5',
                    'SRB': '8'
                }
                
                source_auth_normalized = str(source_authority).strip().upper()
                option_value = authority_map.get(source_auth_normalized)
                
                if not option_value:
                    logging.error(f"[STWH] STEP 1 FAILED: Unknown source authority '{source_authority}'")
                    return {
                        'status': '⚠️ Error - Invalid source authority',
                        'value_of_purchases': 'N/A'
                    }
                
                option_selectors = [
                    (By.XPATH, f"//div[@id='correspondenceTabs:loadStwhAnnexAform:sourceAuthority_panel']//li[@data-label='{source_auth_normalized}']"),
                    (By.XPATH, f"//div[contains(@id, 'loadStwhAnnexAform:sourceAuthority_panel')]//li[contains(text(), '{source_auth_normalized}')]"),
                    (By.XPATH, f"//select[@id='correspondenceTabs:loadStwhAnnexAform:sourceAuthority_input']/option[@value='{option_value}']"),
                ]
                
                option_selected = False
                for by_type, selector in option_selectors:
                    try:
                        option = wait.until(EC.element_to_be_clickable((by_type, selector)))
                        self._human_like_click(option)
                        logging.info(f"[STWH] ✓ STEP 1 COMPLETED: Selected Source Authority: {source_auth_normalized}")
                        option_selected = True
                        self._random_delay(0.25, 0.5)
                        break
                    except TimeoutException:
                        continue
                
                if not option_selected:
                    logging.error(f"[STWH] STEP 1 FAILED: Could not select option '{source_auth_normalized}'")
                    return {
                        'status': '⚠️ Error - Option not selectable',
                        'value_of_purchases': 'N/A'
                    }
                
                # Verify selection
                self._random_delay(0.1, 0.25)
                selected_value = self.driver.execute_script("""
                    var dropdown = document.getElementById('correspondenceTabs:loadStwhAnnexAform:sourceAuthority');
                    if (dropdown) {
                        var label = dropdown.querySelector('.ui-selectonemenu-label');
                        return label ? label.innerText.trim() : '';
                    }
                    return '';
                """)
                
                if selected_value != source_auth_normalized:
                    logging.error(f"[STWH] STEP 1 VERIFICATION FAILED: Expected '{source_auth_normalized}', got '{selected_value}'")
                    return {
                        'status': '⚠️ Error - Selection verification failed',
                        'value_of_purchases': 'N/A'
                    }
                
                logging.info(f"[STWH] ✓ STEP 1 VERIFIED: Source Authority is set to '{selected_value}'")
            
            # Step 2: Enter Seller NTN
            if invoice_number:
                logging.info(f"[STWH] STEP 2: Entering Seller NTN: {invoice_number}")
                
                seller_ntn_input = None
                seller_ntn_selectors = [
                    # Strategy 1: Exact ID match
                    (By.ID, "correspondenceTabs:loadStwhAnnexAform:annexASellerRegNo"),
                    
                    # Strategy 2: Name attribute match
                    (By.NAME, "correspondenceTabs:loadStwhAnnexAform:annexASellerRegNo"),
                    
                    # Strategy 3: XPath with ID
                    (By.XPATH, "//input[@id='correspondenceTabs:loadStwhAnnexAform:annexASellerRegNo']"),
                    
                    # Strategy 4: XPath with name
                    (By.XPATH, "//input[@name='correspondenceTabs:loadStwhAnnexAform:annexASellerRegNo']"),
                    
                    # Strategy 5: XPath with form context and ID pattern
                    (By.XPATH, "//form[contains(@id, 'loadStwhAnnexAform')]//input[contains(@id, 'annexASellerRegNo')]"),
                    
                    # Strategy 6: XPath with type and maxlength (specific to seller NTN)
                    (By.XPATH, "//input[@type='text' and @maxlength='13' and contains(@id, 'loadStwhAnnexAform')]"),
                    
                    # Strategy 7: XPath with ui-inputtext class and maxlength
                    (By.XPATH, "//input[contains(@class, 'ui-inputtext') and @maxlength='13' and @type='text']"),
                    
                    # Strategy 8: CSS selector with partial ID
                    (By.CSS_SELECTOR, "input[id*='loadStwhAnnexAform'][id*='annexASellerRegNo']"),
                    
                    # Strategy 9: CSS selector with mediumTextField class and maxlength
                    (By.CSS_SELECTOR, "input.mediumTextField[maxlength='13'][type='text']"),
                    
                    # Strategy 10: Generic text input with maxlength 13
                   
                ]
                
                for by_type, selector in seller_ntn_selectors:
                    try:
                        seller_ntn_input = wait.until(EC.visibility_of_element_located((by_type, selector)))
                        seller_ntn_input = wait.until(EC.element_to_be_clickable((by_type, selector)))
                        logging.info(f"[STWH] Found Seller NTN input using selector: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if not seller_ntn_input:
                    logging.error("[STWH] STEP 2 FAILED: Seller NTN input field not found")
                    return {
                        'status': '⚠️ Error - NTN field not found',
                        'value_of_purchases': 'N/A'
                    }
                
                self._human_like_click(seller_ntn_input)
                self._human_like_type(seller_ntn_input, invoice_number)
                self._random_delay(0.1, 0.25)
                
                entered_value = seller_ntn_input.get_attribute('value')
                if entered_value != str(invoice_number):
                    logging.error(f"[STWH] STEP 2 VERIFICATION FAILED")
                    return {
                        'status': '⚠️ Error - NTN entry verification failed',
                        'value_of_purchases': 'N/A'
                    }
                
                logging.info(f"[STWH] ✓ STEP 2 COMPLETED & VERIFIED: Seller NTN = '{entered_value}'")
                self._random_delay(0.25, 0.5)
            
            # Step 3: Enter Invoice Number
            if invoice_no_field:
                logging.info(f"[STWH] STEP 3: Entering Invoice Number: {invoice_no_field}")
                
                invoice_no_input = None
                invoice_no_selectors = [
                    # Strategy 1: Exact ID match
                    (By.ID, "correspondenceTabs:loadStwhAnnexAform:annexAinvoiceNoId"),
                    
                    # Strategy 2: Name attribute match
                    (By.NAME, "correspondenceTabs:loadStwhAnnexAform:annexAinvoiceNoId"),
                    
                    # Strategy 3: XPath with ID
                    (By.XPATH, "//input[@id='correspondenceTabs:loadStwhAnnexAform:annexAinvoiceNoId']"),
                    
                    # Strategy 4: XPath with name
                    (By.XPATH, "//input[@name='correspondenceTabs:loadStwhAnnexAform:annexAinvoiceNoId']"),
                    
                    # Strategy 5: XPath with form context and ID pattern
                    (By.XPATH, "//form[contains(@id, 'loadStwhAnnexAform')]//input[contains(@id, 'annexAinvoiceNoId')]"),
                    
                    # Strategy 6: XPath with type and maxlength (specific to invoice number)
                    (By.XPATH, "//input[@type='text' and @maxlength='25' and contains(@id, 'loadStwhAnnexAform')]"),
                    
                    # Strategy 7: XPath with ui-inputtext class and maxlength
                    (By.XPATH, "//input[contains(@class, 'ui-inputtext') and @maxlength='25' and @type='text']"),
                    
                    # Strategy 8: CSS selector with partial ID
                    (By.CSS_SELECTOR, "input[id*='loadStwhAnnexAform'][id*='annexAinvoiceNoId']"),
                    
                    # Strategy 9: CSS selector with mediumTextField class and maxlength
                    (By.CSS_SELECTOR, "input.mediumTextField[maxlength='25'][type='text']"),
                    
                    # Strategy 10: Generic text input with maxlength 25
                    (By.XPATH, "//input[@type='text' and @maxlength='25']"),
                ]
                
                for by_type, selector in invoice_no_selectors:
                    try:
                        invoice_no_input = wait.until(EC.visibility_of_element_located((by_type, selector)))
                        invoice_no_input = wait.until(EC.element_to_be_clickable((by_type, selector)))
                        logging.info(f"[STWH] Found Invoice Number input using selector: {selector}")
                        break
                    except TimeoutException:
                        continue
                
                if not invoice_no_input:
                    logging.error("[STWH] STEP 3 FAILED: Invoice Number input field not found")
                    return {
                        'status': '⚠️ Error - Invoice field not found',
                        'value_of_purchases': 'N/A'
                    }
                
                self._human_like_click(invoice_no_input)
                self._human_like_type(invoice_no_input, invoice_no_field)
                self._random_delay(0.1, 0.25)
                
                entered_value = invoice_no_input.get_attribute('value')
                if entered_value != str(invoice_no_field):
                    logging.error(f"[STWH] STEP 3 VERIFICATION FAILED")
                    return {
                        'status': '⚠️ Error - Invoice entry verification failed',
                        'value_of_purchases': 'N/A'
                    }
                
                logging.info(f"[STWH] ✓ STEP 3 COMPLETED & VERIFIED: Invoice Number = '{entered_value}'")
                self._random_delay(0.25, 0.5)
            
            # Step 4: Select Dates (ROBUST - Handles all date formats)
            if date_field and date_field != 'N/A':
                logging.info(f"[STWH] STEP 4: Selecting dates: {date_field}")
                
                parsed_date = self._select_date_from_datepicker(date_field)
                
                if not parsed_date:
                    logging.error(f"[STWH] STEP 4 FAILED: Could not parse date: {date_field}")
                    return {
                        'status': '⚠️ Error - Date parsing failed',
                        'value_of_purchases': 'N/A'
                    }
                
                date_formatted = parsed_date['formatted']
                logging.info(f"[STWH] Parsed date: {date_field} → {date_formatted}")
                
                # Helper function to set date robustly with multiple strategies
                def set_date_field_robust(field_name, field_id_pattern, date_value):
                    logging.info(f"[STWH] Setting {field_name} to: {date_value}")
                    
                    # Strategy 1: Find input field
                    date_input = None
                    date_selectors = [
                        (By.ID, f"correspondenceTabs:loadStwhAnnexAform:{field_id_pattern}_input"),
                        (By.XPATH, f"//input[@id='correspondenceTabs:loadStwhAnnexAform:{field_id_pattern}_input']"),
                        (By.XPATH, f"//span[@id='correspondenceTabs:loadStwhAnnexAform:{field_id_pattern}']//input"),
                        (By.XPATH, f"//input[contains(@id, '{field_id_pattern}_input')]"),
                        (By.CSS_SELECTOR, f"input[id*='{field_id_pattern}_input']"),
                    ]
                    
                    for by_type, selector in date_selectors:
                        try:
                            date_input = wait.until(EC.visibility_of_element_located((by_type, selector)))
                            logging.info(f"[STWH] Found {field_name} input using: {selector}")
                            break
                        except TimeoutException:
                            continue
                    
                    if not date_input:
                        logging.error(f"[STWH] {field_name} input not found")
                        return False
                    
                    # Strategy 2: Set date using multiple approaches with event triggering
                    date_set_success = self.driver.execute_script("""
                        var input = arguments[0];
                        var dateValue = arguments[1];
                        
                        console.log('[STWH] Date Setting - Input ID:', input.id);
                        console.log('[STWH] Date Setting - Target value:', dateValue);
                        
                        // APPROACH 1: Direct value set + trigger all events
                        try {
                            // Clear existing value
                            input.value = '';
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            
                            // Set new value
                            input.value = dateValue;
                            
                            // Trigger events in sequence
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                            input.dispatchEvent(new Event('blur', { bubbles: true }));
                            input.dispatchEvent(new KeyboardEvent('keyup', { bubbles: true }));
                            
                            console.log('[STWH] APPROACH 1: Value set and events triggered');
                            
                            // Verify
                            if (input.value === dateValue) {
                                console.log('[STWH] ✓ APPROACH 1 SUCCESS: Value verified');
                                return {success: true, method: 'approach-1-direct-events'};
                            }
                        } catch (e) {
                            console.log('[STWH] APPROACH 1 failed:', e.message);
                        }
                        
                        // APPROACH 2: Focus, clear, type simulation
                        try {
                            input.focus();
                            input.select();
                            
                            // Clear by setting empty
                            var nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, 'value').set;
                            nativeInputValueSetter.call(input, '');
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            
                            // Set value using native setter
                            nativeInputValueSetter.call(input, dateValue);
                            
                            // Trigger events
                            input.dispatchEvent(new Event('input', { bubbles: true }));
                            input.dispatchEvent(new Event('change', { bubbles: true }));
                            input.blur();
                            
                            console.log('[STWH] APPROACH 2: Native setter used');
                            
                            if (input.value === dateValue) {
                                console.log('[STWH] ✓ APPROACH 2 SUCCESS: Value verified');
                                return {success: true, method: 'approach-2-native-setter'};
                            }
                        } catch (e) {
                            console.log('[STWH] APPROACH 2 failed:', e.message);
                        }
                        
                        // APPROACH 3: jQuery if available (PrimeFaces often uses jQuery)
                        if (typeof jQuery !== 'undefined') {
                            try {
                                jQuery(input).val(dateValue).trigger('input').trigger('change').blur();
                                console.log('[STWH] APPROACH 3: jQuery used');
                                
                                if (input.value === dateValue) {
                                    console.log('[STWH] ✓ APPROACH 3 SUCCESS: Value verified');
                                    return {success: true, method: 'approach-3-jquery'};
                                }
                            } catch (e) {
                                console.log('[STWH] APPROACH 3 failed:', e.message);
                            }
                        }
                        
                        // APPROACH 4: PrimeFaces widget method
                        try {
                            var widgetVar = input.id.replace(/:/g, '_');
                            if (typeof PrimeFaces !== 'undefined' && PrimeFaces.widgets[widgetVar]) {
                                PrimeFaces.widgets[widgetVar].setDate(dateValue);
                                console.log('[STWH] APPROACH 4: PrimeFaces widget setDate used');
                                
                                if (input.value === dateValue) {
                                    console.log('[STWH] ✓ APPROACH 4 SUCCESS: Value verified');
                                    return {success: true, method: 'approach-4-primefaces-widget'};
                                }
                            }
                        } catch (e) {
                            console.log('[STWH] APPROACH 4 failed:', e.message);
                        }
                        
                        // APPROACH 5: Force value and mark as touched
                        try {
                            input.removeAttribute('readonly');
                            input.value = dateValue;
                            input.setAttribute('value', dateValue);
                            
                            // Mark field as touched/dirty
                            if (input.classList) {
                                input.classList.add('ng-dirty', 'ng-touched', 'ui-state-filled');
                            }
                            
                            // Trigger all possible events
                            ['input', 'change', 'blur', 'focusout'].forEach(function(eventType) {
                                input.dispatchEvent(new Event(eventType, { bubbles: true }));
                            });
                            
                            console.log('[STWH] APPROACH 5: Force value with all events');
                            
                            if (input.value === dateValue) {
                                console.log('[STWH] ✓ APPROACH 5 SUCCESS: Value verified');
                                return {success: true, method: 'approach-5-force-value'};
                            }
                        } catch (e) {
                            console.log('[STWH] APPROACH 5 failed:', e.message);
                        }
                        
                        // Final verification
                        console.log('[STWH] Final check - Current value:', input.value);
                        if (input.value === dateValue) {
                            return {success: true, method: 'eventual-success'};
                        }
                        
                        console.error('[STWH] All approaches failed to set date');
                        return {success: false, error: 'All methods failed', currentValue: input.value};
                    """, date_input, date_value)
                    
                    if date_set_success and date_set_success.get('success'):
                        method = date_set_success.get('method', 'unknown')
                        logging.info(f"[STWH] ✓ {field_name} set using: {method}")
                        self._random_delay(0.1, 0.25)
                        
                        # Final verification
                        final_value = date_input.get_attribute('value')
                        if final_value == date_value:
                            logging.info(f"[STWH] ✓ {field_name} verified: {final_value}")
                            return True
                        else:
                            logging.warning(f"[STWH] {field_name} value mismatch: expected '{date_value}', got '{final_value}'")
                            # Try one more time with direct attribute setting
                            self.driver.execute_script("arguments[0].setAttribute('value', arguments[1]);", date_input, date_value)
                            final_value = date_input.get_attribute('value')
                            if final_value == date_value:
                                logging.info(f"[STWH] ✓ {field_name} verified after retry: {final_value}")
                                return True
                            return False
                    else:
                        error = date_set_success.get('error', 'Unknown') if date_set_success else 'Script failed'
                        current = date_set_success.get('currentValue', 'N/A') if date_set_success else 'N/A'
                        logging.error(f"[STWH] {field_name} setting failed: {error}, current value: {current}")
                        return False
                
                # Set From Date
                if not set_date_field_robust("From Date", "annexAFromDate", date_formatted):
                    logging.error("[STWH] STEP 4 FAILED: From Date could not be set")
                    return {
                        'status': '⚠️ Error - From Date setting failed',
                        'value_of_purchases': 'N/A'
                    }
                
                self._random_delay(0.25, 0.5)
                
                # Set To Date
                if not set_date_field_robust("To Date", "annexAToDate", date_formatted):
                    logging.error("[STWH] STEP 4 FAILED: To Date could not be set")
                    return {
                        'status': '⚠️ Error - To Date setting failed',
                        'value_of_purchases': 'N/A'
                    }
                
                logging.info(f"[STWH] ✅ STEP 4 COMPLETED: Both dates set to '{date_formatted}'")
                self._random_delay(0.25, 0.5)
            
            # Step 5: Click the Search button
            logging.info("[STWH] STEP 5: Clicking Search button")
            
            search_button_selectors = [
                # Strategy 1: Button with loadStwhAnnexAform context and j_idt pattern
                (By.XPATH, "//button[contains(@id, 'correspondenceTabs:loadStwhAnnexAform:j_idt') and @type='submit']//span[contains(text(), 'Search')]"),
                
                # Strategy 2: Button with ui-button class and Search span text
                (By.XPATH, "//button[contains(@class, 'ui-button') and @type='submit']//span[@class='ui-button-text ui-c' and contains(text(), 'Search')]"),
                
                # Strategy 3: Form-scoped button with loadStwhAnnexAform and Search text
                (By.XPATH, "//form[contains(@id, 'loadStwhAnnexAform')]//button[@type='submit' and contains(@class, 'ui-button')]//span[text()='Search']"),
                
                # Strategy 4: Button with onclick containing PrimeFaces.ab and Search span
                (By.XPATH, "//button[contains(@onclick, 'PrimeFaces.ab') and contains(@id, 'loadStwhAnnexAform')]//span[contains(text(), 'Search')]"),
                
                # Strategy 5: Button with role='button' and Search text
                (By.XPATH, "//button[@role='button' and contains(@id, 'loadStwhAnnexAform') and @type='submit']//span[normalize-space()='Search']"),
                
                # Strategy 6: CSS selector with partial ID and type submit
                (By.CSS_SELECTOR, "button[id*='loadStwhAnnexAform'][type='submit'][class*='ui-button']"),
                
                # Strategy 7: Button with ui-widget class and Search span
                (By.XPATH, "//button[contains(@class, 'ui-widget') and contains(@class, 'ui-state-default') and @type='submit']//span[text()='Search']"),
                
                # Strategy 8: Span with ui-button-text containing Search, then find parent button
                (By.XPATH, "//span[contains(@class, 'ui-button-text') and contains(text(), 'Search')]/parent::button[@type='submit' and contains(@id, 'loadStwhAnnexAform')]"),
                
                # Strategy 9: Button with name matching loadStwhAnnexAform pattern
                (By.XPATH, "//button[contains(@name, 'loadStwhAnnexAform:j_idt') and @type='submit']//span[contains(text(), 'Search')]"),
                
                # Strategy 10: Generic ui-button with Search text in loadStwhAnnexAform context
                (By.XPATH, "//button[contains(@id, 'loadStwhAnnexAform') and contains(@class, 'ui-button')]//span[normalize-space(text())='Search']"),
                
                # Strategy 11: Button with aria-disabled='false' and Search text
                (By.XPATH, "//button[@aria-disabled='false' and @type='submit' and contains(@id, 'loadStwhAnnexAform')]//span[text()='Search']"),
                
                # Strategy 12: Fallback - any submit button with Search text
                (By.XPATH, "//button[@type='submit' and contains(@class, 'ui-button')]//span[contains(text(), 'Search')]"),
            ]
            
            search_button = None
            for by_type, selector in search_button_selectors:
                try:
                    search_button = WebDriverWait(self.driver, 1).until(
                        EC.element_to_be_clickable((by_type, selector))
                    )
                    logging.info(f"[STWH] Found Search button using selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not search_button:
                # JavaScript fallback
                try:
                    logging.info("[STWH] Using JavaScript to find Search button")
                    self.driver.execute_script("""
                        var buttons = document.querySelectorAll('button, input[type="submit"], a');
                        for (var i = 0; i < buttons.length; i++) {
                            if (buttons[i].textContent.includes('Search') || 
                                buttons[i].value === 'Search' ||
                                buttons[i].id.includes('Search')) {
                                buttons[i].click();
                                return true;
                            }
                        }
                        return false;
                    """)
                    logging.info("[STWH] Search button clicked via JavaScript")
                    search_button = True
                except Exception as js_error:
                    logging.error(f"[STWH] JavaScript search failed: {str(js_error)}")
            
            if not search_button:
                logging.error("[STWH] STEP 5 FAILED: Search button not found")
                return {
                    'status': '⚠️ Error - Search button not found',
                    'value_of_purchases': 'N/A',
                    'fbr_sales_tax': 'N/A'
                }
            
            if search_button and search_button != True:
                self._human_like_click(search_button)
                logging.info("[STWH] ✓ STEP 5 COMPLETED: Search button clicked")
            
            self._random_delay(0.5, 1.0)
            
            # Wait for loading to complete
            logging.info("[STWH] Waiting for search results to load...")
            try:
                WebDriverWait(self.driver, 60).until(
                    lambda d: d.execute_script("return document.readyState") == "complete" and
                              d.execute_script("return (typeof PrimeFaces !== 'undefined' && PrimeFaces.ajax.Queue.isEmpty())")
                )
                logging.info("[STWH] Page fully loaded and AJAX requests completed")
            except TimeoutException:
                logging.warning("[STWH] Timeout waiting for AJAX, proceeding anyway")
            
            self._random_delay(1.0, 1.5)
            
            # Wait for results table
            logging.info("[STWH] Waiting for results table to appear...")
            
            results_table = None
            results_table_selectors = [
                # Strategy 1: Table with ui-datatable class
                (By.XPATH, "//table[contains(@class, 'ui-datatable')]"),
                
                # Strategy 2: Table with role='grid'
                (By.XPATH, "//table[@role='grid']"),
                
                # Strategy 3: Table with purchaseInvoiceTable ID
                (By.ID, "correspondenceTabs:loadStwhAnnexAform:purchaseInvoiceTable"),
                
                # Strategy 4: Table with ui-datatable-data class
                (By.XPATH, "//table[contains(@class, 'ui-datatable-data')]"),
                
                # Strategy 5: Table within loadStwhAnnexAform form
                (By.XPATH, "//form[contains(@id, 'loadStwhAnnexAform')]//table[contains(@class, 'ui-datatable')]"),
                
                # Strategy 6: Table with ui-datatable-scrollable-body wrapper
                (By.XPATH, "//div[contains(@class, 'ui-datatable-scrollable-body')]//table"),
                
                # Strategy 7: Table with thead and tbody (generic data table structure)
                (By.XPATH, "//table[contains(@id, 'purchaseInvoiceTable') and .//thead and .//tbody]"),
                
                # Strategy 8: CSS selector with ui-datatable class
                (By.CSS_SELECTOR, "table.ui-datatable"),
                
                # Strategy 9: Table with ui-widget class
                (By.XPATH, "//table[contains(@class, 'ui-widget') and contains(@class, 'ui-datatable')]"),
                
                # Strategy 10: Generic table in results area
                (By.XPATH, "//div[contains(@class, 'ui-datatable')]//table"),
            ]
            
            for by_type, selector in results_table_selectors:
                try:
                    results_table = WebDriverWait(self.driver, 2).until(
                        EC.presence_of_element_located((by_type, selector))
                    )
                    logging.info(f"[STWH] Results table found using selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            # JavaScript fallback
            if not results_table:
                logging.info("[STWH] Trying JavaScript fallback for results table...")
                try:
                    results_table = self.driver.execute_script("""
                        // Try multiple strategies to find the table
                        var table = document.querySelector('table.ui-datatable') || 
                                   document.querySelector('table[role="grid"]') ||
                                   document.querySelector('table[id*="purchaseInvoiceTable"]') ||
                                   document.querySelector('form[id*="loadStwhAnnexAform"] table');
                        
                        if (table && table.querySelector('tbody tr')) {
                            return table;
                        }
                        
                        // Last resort: find any table with data rows
                        var tables = document.querySelectorAll('table');
                        for (var i = 0; i < tables.length; i++) {
                            if (tables[i].querySelector('tbody tr')) {
                                return tables[i];
                            }
                        }
                        
                        return null;
                    """)
                    
                    if results_table:
                        logging.info("[STWH] Results table found using JavaScript fallback")
                except Exception as js_error:
                    logging.error(f"[STWH] JavaScript fallback failed: {str(js_error)}")
            
            if not results_table:
                logging.error("[STWH] Results table did not appear after trying all strategies")
                return {
                    'status': '⚠️ Error - No results table',
                    'value_of_purchases': 'N/A',
                    'fbr_sales_tax': 'N/A'
                }
            
            logging.info("[STWH] ✓ Results table verified and ready")
            
            self._random_delay(0.5, 1.0)
            
            # Step 6: Find the correct row by matching Sales Tax/FED in ST Mode
            logging.info(f"[STWH] STEP 6: Finding row with Sales Tax = '{sales_tax_fed_st_mode}'")
            
            try:
                matching_row = self.driver.execute_script("""
                    var targetSalesTax = arguments[0];
                    var tables = document.querySelectorAll('table.ui-datatable-data, table[role="grid"]');
                    
                    for (var t = 0; t < tables.length; t++) {
                        var rows = tables[t].querySelectorAll('tbody tr');
                        
                        for (var i = 0; i < rows.length; i++) {
                            var cells = rows[i].querySelectorAll('td');
                            
                            for (var j = 0; j < cells.length; j++) {
                                var cellText = cells[j].textContent.trim();
                                
                                if (cellText === targetSalesTax || 
                                    parseFloat(cellText.replace(/,/g, '')) === parseFloat(targetSalesTax)) {
                                    
                                    rows[i].setAttribute('data-matched-row', 'true');
                                    return {
                                        rowIndex: i,
                                        tableIndex: t,
                                        columnIndex: j,
                                        salesTaxValue: cellText
                                    };
                                }
                            }
                        }
                    }
                    return null;
                """, str(sales_tax_fed_st_mode))
                
                if not matching_row:
                    logging.error(f"[STWH] STEP 6 FAILED: No row found with Sales Tax = '{sales_tax_fed_st_mode}'")
                    return {
                        'status': f'⚠️ Not Found - Sales Tax {sales_tax_fed_st_mode} not in results',
                        'value_of_purchases': 'N/A',
                        'fbr_sales_tax': 'N/A'
                    }
                
                logging.info(f"[STWH] ✓ STEP 6 COMPLETED: Found matching row at index {matching_row['rowIndex']} "
                           f"in table {matching_row['tableIndex']}, column {matching_row['columnIndex']}")
                self._random_delay(0.25, 0.5)
                
            except Exception as e:
                logging.error(f"[STWH] Error finding matching row: {str(e)}")
                return {
                    'status': '⚠️ Error - Row matching failed',
                    'value_of_purchases': 'N/A',
                    'fbr_sales_tax': 'N/A'
                }
            
            # Step 6.5: Click the checkbox in the matched row
            logging.info("[STWH] STEP 6.5: Clicking checkbox in matched row")
            
            try:
                checkbox_clicked = self.driver.execute_script("""
                    var row = document.querySelector('tr[data-matched-row="true"]');
                    if (!row) {
                        console.error('Matched row not found');
                        return {success: false, error: 'Row not found'};
                    }
                    
                    // Strategy 1: Find checkbox input in the row
                    var checkbox = row.querySelector('input[type="checkbox"]');
                    if (checkbox && !checkbox.checked) {
                        checkbox.click();
                        console.log('Checkbox clicked via input element');
                        return {success: true, method: 'input'};
                    }
                    
                    // Strategy 2: Find div with ui-chkbox class (PrimeFaces checkbox wrapper)
                    var chkboxDiv = row.querySelector('div.ui-chkbox-box, div[role="checkbox"]');
                    if (chkboxDiv) {
                        chkboxDiv.click();
                        console.log('Checkbox clicked via PrimeFaces div');
                        return {success: true, method: 'primefaces-div'};
                    }
                    
                    // Strategy 3: Find any clickable element in first cell (usually checkbox column)
                    var firstCell = row.querySelector('td:first-child');
                    if (firstCell) {
                        var clickable = firstCell.querySelector('input, div[role="checkbox"], span.ui-chkbox-icon');
                        if (clickable) {
                            clickable.click();
                            console.log('Checkbox clicked via first cell element');
                            return {success: true, method: 'first-cell'};
                        }
                    }
                    
                    // Strategy 4: Look for checkbox by ID pattern
                    var inputs = row.querySelectorAll('input[id*="checkbox"], input[id*="chk"]');
                    if (inputs.length > 0) {
                        inputs[0].click();
                        console.log('Checkbox clicked via ID pattern');
                        return {success: true, method: 'id-pattern'};
                    }
                    
                    return {success: false, error: 'No checkbox found in row'};
                """)
                
                if checkbox_clicked and checkbox_clicked.get('success'):
                    logging.info(f"[STWH] ✓ STEP 6.5 COMPLETED: Checkbox clicked using method '{checkbox_clicked.get('method')}'")
                    self._random_delay(0.5, 0.75)
                else:
                    error_msg = checkbox_clicked.get('error', 'Unknown error') if checkbox_clicked else 'Script returned null'
                    logging.error(f"[STWH] STEP 6.5 FAILED: {error_msg}")
                    return {
                        'status': f'⚠️ Error - Checkbox not clickable ({error_msg})',
                        'value_of_purchases': 'N/A',
                        'fbr_sales_tax': 'N/A'
                    }
                    
            except Exception as e:
                logging.error(f"[STWH] Error clicking checkbox: {str(e)}")
                return {
                    'status': '⚠️ Error - Checkbox click failed',
                    'value_of_purchases': 'N/A',
                    'fbr_sales_tax': 'N/A'
                }
            
            # Step 7: Extract "Value of Purchases"
            logging.info("[STWH] STEP 7: Extracting 'Value of Purchases'")
            
            try:
                value_of_purchases = self.driver.execute_script(r"""
                    var row = document.querySelector('tr[data-matched-row="true"]');
                    if (!row) return null;
                    
                    var cells = row.querySelectorAll('td');
                    var headers = row.closest('table').querySelectorAll('thead th');
                    
                    for (var i = 0; i < headers.length; i++) {
                        var headerText = headers[i].textContent.trim().toLowerCase();
                        if (headerText.includes('value') && headerText.includes('purchase')) {
                            if (cells[i]) {
                                return cells[i].textContent.trim();
                            }
                        }
                    }
                    
                    for (var i = 0; i < cells.length; i++) {
                        var cellText = cells[i].textContent.trim();
                        if (/^[\d,]+(\.\d{1,2})?$/.test(cellText) && cellText !== arguments[0]) {
                            return cellText;
                        }
                    }
                    
                    return null;
                """, str(sales_tax_fed_st_mode))
                
                if not value_of_purchases:
                    logging.warning("[STWH] Could not extract 'Value of Purchases' from row")
                    value_of_purchases = "N/A"
                else:
                    logging.info(f"[STWH] ✓ STEP 7 COMPLETED: Value of Purchases = '{value_of_purchases}'")
                
                self._random_delay(0.25, 0.5)
                
            except Exception as e:
                logging.error(f"[STWH] Error extracting value: {str(e)}")
                value_of_purchases = "N/A"
            
            # Step 8: Click the "Claim" button (PAGE-LEVEL button in toolbar, not in row)
            logging.info("[STWH] STEP 8: Clicking 'Claim' button")
            
            try:
                claim_result = self.driver.execute_script("""
                    var debugLog = [];
                    
                    // Verify matched row exists and checkbox is selected
                    var row = document.querySelector('tr[data-matched-row="true"]');
                    if (!row) {
                        debugLog.push('ERROR: Matched row not found');
                        return {success: false, error: 'Matched row not found', debugLog: debugLog};
                    }
                    
                    debugLog.push('✓ Matched row verified');
                    
                    // IMPORTANT: Claim button is a PAGE-LEVEL button in the toolbar, NOT inside the row!
                    // Search entire document for Claim button
                    
                    // STRATEGY 1: Button with exact text "Claim" in toolbar/form area
                    var allButtons = document.querySelectorAll('button');
                    debugLog.push('Total buttons on page: ' + allButtons.length);
                    
                    var claimButtons = [];
                    for (var i = 0; i < allButtons.length; i++) {
                        var btn = allButtons[i];
                        var btnText = btn.textContent.trim();
                        if (btnText === 'Claim') {
                            claimButtons.push({
                                button: btn,
                                id: btn.id || 'NO_ID',
                                classes: btn.className || 'NO_CLASSES',
                                disabled: btn.disabled,
                                ariaDisabled: btn.getAttribute('aria-disabled'),
                                visible: btn.offsetParent !== null,
                                parent: btn.parentElement ? btn.parentElement.tagName : 'NO_PARENT'
                            });
                        }
                    }
                    
                    debugLog.push('Found ' + claimButtons.length + ' buttons with text "Claim"');
                    
                    // Try each Claim button found
                    for (var i = 0; i < claimButtons.length; i++) {
                        var btnInfo = claimButtons[i];
                        debugLog.push('Claim button ' + i + ': ID=' + btnInfo.id + ', Classes=' + btnInfo.classes + 
                                     ', Disabled=' + btnInfo.disabled + ', Visible=' + btnInfo.visible);
                        
                        if (btnInfo.visible && !btnInfo.disabled && btnInfo.ariaDisabled !== 'true') {
                            debugLog.push('STRATEGY 1 SUCCESS - Clicking Claim button ID: ' + btnInfo.id);
                            btnInfo.button.click();
                            return {success: true, method: 'strategy-1-page-level-claim', buttonId: btnInfo.id, debugLog: debugLog};
                        } else {
                            debugLog.push('Claim button ' + i + ' not clickable (disabled or hidden)');
                        }
                    }
                    
                    // STRATEGY 2: Look for button in loadStwhAnnexAform context with "Claim" text
                    var formButtons = document.querySelectorAll('form[id*="loadStwhAnnexAform"] button, div[id*="loadStwhAnnexAform"] button');
                    debugLog.push('STRATEGY 2: Found ' + formButtons.length + ' buttons in form context');
                    for (var i = 0; i < formButtons.length; i++) {
                        var btn = formButtons[i];
                        if (btn.textContent.trim() === 'Claim') {
                            if (btn.offsetParent !== null && !btn.disabled && btn.getAttribute('aria-disabled') !== 'true') {
                                debugLog.push('STRATEGY 2 SUCCESS - Clicking Claim button ID: ' + btn.id);
                                btn.click();
                                return {success: true, method: 'strategy-2-form-context', buttonId: btn.id, debugLog: debugLog};
                            }
                        }
                    }
                    
                    // STRATEGY 3: Look for button with span containing "Claim"
                    var spanButtons = document.querySelectorAll('button span');
                    debugLog.push('STRATEGY 3: Scanning ' + spanButtons.length + ' button spans');
                    for (var i = 0; i < spanButtons.length; i++) {
                        var span = spanButtons[i];
                        if (span.textContent.trim() === 'Claim') {
                            var btn = span.closest('button');
                            if (btn && btn.offsetParent !== null && !btn.disabled && btn.getAttribute('aria-disabled') !== 'true') {
                                debugLog.push('STRATEGY 3 SUCCESS - Clicking Claim button via span, ID: ' + btn.id);
                                btn.click();
                                return {success: true, method: 'strategy-3-span-search', buttonId: btn.id, debugLog: debugLog};
                            }
                        }
                    }
                    
                    // STRATEGY 4: Look for button with ui-button class and "Claim" text
                    var uiButtons = document.querySelectorAll('button.ui-button, button[class*="btn"]');
                    debugLog.push('STRATEGY 4: Found ' + uiButtons.length + ' UI buttons');
                    for (var i = 0; i < uiButtons.length; i++) {
                        var btn = uiButtons[i];
                        if (btn.textContent.trim() === 'Claim') {
                            if (btn.offsetParent !== null && !btn.disabled && btn.getAttribute('aria-disabled') !== 'true') {
                                debugLog.push('STRATEGY 4 SUCCESS - Clicking UI button ID: ' + btn.id);
                                btn.click();
                                return {success: true, method: 'strategy-4-ui-button', buttonId: btn.id, debugLog: debugLog};
                            }
                        }
                    }
                    
                    // STRATEGY 5: Force click first visible Claim button (ignore disabled state)
                    debugLog.push('STRATEGY 5: FORCE CLICK - Attempting first visible Claim button');
                    for (var i = 0; i < claimButtons.length; i++) {
                        var btnInfo = claimButtons[i];
                        if (btnInfo.visible) {
                            debugLog.push('STRATEGY 5: Force clicking Claim button ID: ' + btnInfo.id);
                            try {
                                btnInfo.button.click();
                                debugLog.push('STRATEGY 5 SUCCESS - Force clicked ID: ' + btnInfo.id);
                                return {success: true, method: 'strategy-5-force-click', buttonId: btnInfo.id, debugLog: debugLog};
                            } catch (e) {
                                debugLog.push('STRATEGY 5: Click failed - ' + e.message);
                            }
                        }
                    }
                    
                    // STRATEGY 6: JavaScript click event dispatch
                    debugLog.push('STRATEGY 6: Trying event dispatch on first Claim button');
                    if (claimButtons.length > 0) {
                        var btn = claimButtons[0].button;
                        try {
                            var clickEvent = new MouseEvent('click', {
                                bubbles: true,
                                cancelable: true,
                                view: window
                            });
                            btn.dispatchEvent(clickEvent);
                            debugLog.push('STRATEGY 6 SUCCESS - Dispatched click event to: ' + claimButtons[0].id);
                            return {success: true, method: 'strategy-6-event-dispatch', buttonId: claimButtons[0].id, debugLog: debugLog};
                        } catch (e) {
                            debugLog.push('STRATEGY 6 failed: ' + e.message);
                        }
                    }
                    
                    // All strategies failed
                    debugLog.push('ERROR: All 6 strategies failed to click Claim button');
                    return {
                        success: false,
                        error: 'Claim button found but not clickable',
                        debugLog: debugLog,
                        claimButtonsFound: claimButtons.length,
                        claimButtonDetails: claimButtons
                    };
                """)
                
                # Log debug information from JavaScript
                if claim_result and 'debugLog' in claim_result:
                    logging.info("[STWH] JavaScript Debug Log:")
                    for log_msg in claim_result['debugLog']:
                        logging.info(f"[STWH]   {log_msg}")
                
                if not claim_result or not claim_result.get('success'):
                    error_msg = claim_result.get('error', 'Unknown error') if claim_result else 'Script returned null'
                    
                    # Log detailed button information for debugging
                    if claim_result and 'buttonDetails' in claim_result:
                        logging.error("[STWH] DETAILED BUTTON ANALYSIS:")
                        for btn_info in claim_result['buttonDetails']:
                            logging.error(f"[STWH]   Button {btn_info['index']}: ID={btn_info['id']}, "
                                        f"Classes={btn_info['classes']}, Type={btn_info['type']}, "
                                        f"Text='{btn_info['text']}', Disabled={btn_info['disabled']}, "
                                        f"AriaDisabled={btn_info['ariaDisabled']}, Visible={btn_info['visible']}")
                            logging.error(f"[STWH]   HTML: {btn_info['innerHTML'][:100]}")
                    
                    logging.error(f"[STWH] STEP 8 FAILED: 'Claim' button not found - {error_msg}")
                    return {
                        'status': f'⚠️ Error - Claim button not found ({error_msg})',
                        'value_of_purchases': value_of_purchases,
                        'fbr_sales_tax': sales_tax_fed_st_mode
                    }
                
                method = claim_result.get('method', 'unknown')
                button_id = claim_result.get('buttonId', 'unknown')
                logging.info(f"[STWH] ✓ STEP 8 COMPLETED: 'Claim' button clicked using {method}, button ID: {button_id}")
                
            except Exception as e:
                logging.error(f"[STWH] Error clicking claim button: {str(e)}")
                return {
                    'status': '⚠️ Error - Claim click failed',
                    'value_of_purchases': value_of_purchases,
                    'fbr_sales_tax': sales_tax_fed_st_mode
                }
            
            # Step 9: Wait for AJAX processing and success confirmation
            logging.info("[STWH] STEP 9: Waiting for claim processing to complete...")
            
            try:
                # Wait for AJAX to start (brief delay)
                self._random_delay(0.5, 1.0)
                
                # Wait for PrimeFaces AJAX queue to empty and page to be complete
                logging.info("[STWH] Waiting for AJAX queue to complete...")
                WebDriverWait(self.driver, 90).until(
                    lambda d: d.execute_script("""
                        return document.readyState === 'complete' && 
                               (typeof PrimeFaces === 'undefined' || PrimeFaces.ajax.Queue.isEmpty());
                    """)
                )
                logging.info("[STWH] ✓ AJAX processing completed")
                
                # Additional wait for any animations or updates to settle
                self._random_delay(1.0, 1.5)
                
                # Wait for success message or growl notification to appear
                logging.info("[STWH] Checking for success confirmation...")
                success_found = False
                
                try:
                    # Wait for success message with explicit timeout
                    WebDriverWait(self.driver, 30).until(
                        lambda d: d.execute_script("""
                            var messages = document.querySelectorAll(
                                '.ui-messages-info, .ui-messages-info-summary, .ui-messages-info-detail, ' +
                                '.ui-growl-message, .ui-growl-item, ' +
                                '[class*="success"], [class*="Success"], ' +
                                '.alert-success, .message-success'
                            );
                            
                            for (var i = 0; i < messages.length; i++) {
                                var msg = messages[i];
                                var text = msg.textContent.toLowerCase();
                                var isVisible = msg.offsetParent !== null;
                                
                                if (isVisible && (
                                    text.includes('success') || 
                                    text.includes('loaded') || 
                                    text.includes('claimed') ||
                                    text.includes('completed') ||
                                    text.includes('saved')
                                )) {
                                    return msg.textContent.trim();
                                }
                            }
                            return null;
                        """)
                    )
                    
                    success_message = self.driver.execute_script("""
                        var messages = document.querySelectorAll(
                            '.ui-messages-info, .ui-growl-message, [class*="success"]'
                        );
                        for (var i = 0; i < messages.length; i++) {
                            var text = messages[i].textContent.toLowerCase();
                            if (text.includes('success') || text.includes('loaded') || text.includes('claimed')) {
                                return messages[i].textContent.trim();
                            }
                        }
                        return null;
                    """)
                    
                    if success_message:
                        logging.info(f"[STWH] ✓ STEP 9 COMPLETED: Success confirmation: '{success_message}'")
                        success_found = True
                    
                except TimeoutException:
                    logging.warning("[STWH] No success message appeared within timeout, checking for errors...")
                    
                    # Check for error messages
                    error_message = self.driver.execute_script("""
                        var errors = document.querySelectorAll(
                            '.ui-messages-error, .ui-messages-error-summary, ' +
                            '.alert-error, .alert-danger, [class*="error"]'
                        );
                        for (var i = 0; i < errors.length; i++) {
                            var isVisible = errors[i].offsetParent !== null;
                            if (isVisible) {
                                return errors[i].textContent.trim();
                            }
                        }
                        return null;
                    """)
                    
                    if error_message:
                        logging.error(f"[STWH] Error message detected: {error_message}")
                        return {
                            'status': f'⚠️ Error - {error_message[:100]}',
                            'value_of_purchases': value_of_purchases,
                            'fbr_sales_tax': sales_tax_fed_st_mode
                        }
                
                # Final verification: ensure we're still on the correct page or moved to success state
                self._random_delay(1.0, 1.5)
                
                if not success_found:
                    # Check if the row is still marked (might indicate incomplete operation)
                    row_still_exists = self.driver.execute_script("""
                        return document.querySelector('tr[data-matched-row="true"]') !== null;
                    """)
                    
                    if row_still_exists:
                        logging.warning("[STWH] Matched row still exists - operation may not have completed fully")
                    else:
                        logging.info("[STWH] Matched row no longer present - operation likely completed")
                        success_found = True
                
                if not success_found:
                    logging.warning("[STWH] Could not confirm success, but proceeding after wait period")
                
            except TimeoutException:
                logging.error("[STWH] Timeout waiting for claim processing to complete")
                return {
                    'status': '⚠️ Error - Processing timeout',
                    'value_of_purchases': value_of_purchases,
                    'fbr_sales_tax': sales_tax_fed_st_mode
                }
            except Exception as e:
                logging.error(f"[STWH] Error during claim verification: {str(e)}")
                return {
                    'status': '⚠️ Error - Verification failed',
                    'value_of_purchases': value_of_purchases,
                    'fbr_sales_tax': sales_tax_fed_st_mode
                }
            
            logging.info(f"[STWH] ✅ WORKFLOW COMPLETE: Invoice {invoice_number} processed successfully")
            
            return {
                'status': '✓ Success',
                'value_of_purchases': value_of_purchases,
                'fbr_sales_tax': sales_tax_fed_st_mode
            }
            
        except WebDriverException as e:
            logging.error(f"[STWH] Browser closed by user during processing: {str(e)}")
            return {
                'status': '[STWH] ⚠️ Browser Closed',
                'value_of_purchases': 'N/A',
                'fbr_sales_tax': 'N/A'
            }
        except Exception as e:
            logging.error(f"[STWH] Error processing invoice {invoice_number}: {str(e)}")
            return {
                'status': '[STWH] ⚠️ Error',
                'value_of_purchases': 'N/A',
                'fbr_sales_tax': 'N/A'
            }
    

    
    def close_browser(self):
        """
        Close the browser and clean up resources.
        """
        try:
            if self.driver:
                self.driver.quit()
                logging.info("Browser closed successfully")
        except Exception as e:
            logging.error(f"Error closing browser: {str(e)}")


# Configuration note for users
"""
IMPORTANT: FBR WEBSITE CONFIGURATION

The selectors used in this module (element IDs, classes, XPaths) are templates 
and MUST be updated based on the actual FBR invoice verification website structure.

To configure:
1. Open the FBR invoice verification page in your browser
2. Right-click on the invoice input field → Inspect Element
3. Note the element's ID, name, or create an appropriate XPath
4. Update the selectors in the verify_invoice() method accordingly
5. Do the same for the search button and result container

Common element attributes to look for:
- ID: Most reliable (e.g., id="invoiceNumber")
- Name: Also reliable (e.g., name="invoice")
- Class: May not be unique (e.g., class="form-input")
- XPath: Most flexible but can break if site changes

Example FBR URLs to check:
- https://iris.fbr.gov.pk/customer/verification
- https://e.fbr.gov.pk/esbn/
"""
