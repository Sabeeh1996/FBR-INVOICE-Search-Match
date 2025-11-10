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


class FBRChecker:
    """
    Automates invoice verification on FBR portal using Selenium WebDriver.
    """
    
    # FBR Sales Tax Invoice Management URL
    FBR_URL = "https://irisv1.fbr.gov.pk/salesTax/invoices/index.xhtml?mode=3D2EAF95F000134C2BD2036C42962F48&task=270"
    
    def __init__(self):
        """
        Initialize the FBR Checker with Selenium WebDriver.
        """
        self.driver = None
        self.max_retries = 3
        self.actions = None  # ActionChains for mouse movements
        
    def initialize_browser(self):
        """
        Initialize Chrome browser with appropriate options.
        
        Returns:
            bool: True if browser initialized successfully, False otherwise
        """
        try:
            # Use undetected-chromedriver for maximum stealth
            # This patches the Chrome executable to remove all Selenium/WebDriver indicators
            options = uc.ChromeOptions()
            options.add_argument('--start-maximized')
            options.add_argument('--no-first-run')
            options.add_argument('--no-default-browser-check')
            options.add_argument('--disable-popup-blocking')
            
            # Additional stealth arguments
            options.add_argument('--disable-blink-features=AutomationControlled')
            options.add_argument('--disable-infobars')
            options.add_argument('--disable-browser-side-navigation')
            
            # Fix SSL handshake errors
            options.add_argument('--ignore-certificate-errors')
            options.add_argument('--ignore-ssl-errors')
            options.add_argument('--allow-insecure-localhost')
            options.add_argument('--disable-web-security')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # Disable GPU for stability
            options.add_argument('--disable-gpu')
            
            # Suppress console logging
            options.add_argument('--log-level=3')
            
            # Note: undetected-chromedriver doesn't use experimental_option for excludeSwitches
            # It handles stealth internally, so we avoid conflicting options
            
            # Disable password manager and notifications
            prefs = {
                "profile.default_content_setting_values.notifications": 2,
                "credentials_enable_service": False,
                "profile.password_manager_enabled": False
            }
            options.add_experimental_option("prefs", prefs)
            
            # Initialize undetected Chrome driver
            # version_main=None allows it to auto-detect Chrome version
            # use_subprocess=False prevents multiprocessing issues on Windows
            self.driver = uc.Chrome(options=options, version_main=None)
            
            # Additional JavaScript injections for complete stealth
            self.driver.execute_script("""
                // Override navigator properties
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                });
                
                Object.defineProperty(navigator, 'chromeVersion', {
                    get: () => undefined
                });
                
                Object.defineProperty(navigator, 'vendor', {
                    get: () => 'Google Inc.'
                });
                
                // Mock chrome object
                window.chrome = {
                    runtime: {}
                };
                
                // Hide headless browser indicators
                window.outerHeight = 1040;
                window.outerWidth = 1920;
            """)
            
            # Set implicit wait
            self.driver.implicitly_wait(10)
            
            # Initialize ActionChains
            self.actions = ActionChains(self.driver)
            
            logging.info("✅ Chrome browser initialized with MAXIMUM stealth mode (undetected-chromedriver)")
            logging.info("🔒 All Selenium automation markers have been removed")
            return True
            
        except Exception as e:
            logging.error(f"Failed to initialize Chrome browser: {str(e)}")
            logging.error("Make sure to run: pip install undetected-chromedriver")
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
        self._random_delay(0.3, 0.7)
        
        for char in str(text):
            element.send_keys(char)
            # Random typing speed between 50-150ms per character
            time.sleep(random.uniform(0.05, 0.15))
        
        # Small pause after typing
        self._random_delay(0.3, 0.8)
    
    def _human_like_click(self, element):
        """
        Click element with mouse movement to simulate human behavior.
        
        Args:
            element: WebElement to click
        """
        try:
            # Scroll element into view
            self.driver.execute_script("arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});", element)
            self._random_delay(0.5, 1.0)
            
            # Move mouse to element with smooth movement
            self.actions.move_to_element(element).perform()
            self._random_delay(0.3, 0.7)
            
            # Click using ActionChains (more human-like than element.click())
            self.actions.click(element).perform()
            
            logging.debug("Performed human-like click")
            
        except Exception as e:
            # Fallback to regular click if ActionChains fails
            logging.warning(f"ActionChains click failed, using fallback: {str(e)}")
            element.click()
    
    def _simulate_mouse_movement(self):
        """
        Simulate random mouse movements to appear more human-like.
        """
        try:
            # Random small mouse movements
            for _ in range(random.randint(1, 3)):
                x_offset = random.randint(-100, 100)
                y_offset = random.randint(-100, 100)
                self.actions.move_by_offset(x_offset, y_offset).perform()
                time.sleep(random.uniform(0.1, 0.3))
        except Exception:
            pass  # Ignore errors in mouse simulation
    
    def navigate_to_fbr(self):
        """
        Navigate to the FBR invoice verification portal.
        
        Returns:
            bool: True if navigation successful, False otherwise
        """
        try:
            self.driver.get(self.FBR_URL)
            logging.info(f"Navigated to FBR portal: {self.FBR_URL}")
            
            # Random delay to simulate page reading
            self._random_delay(2.0, 4.0)
            
            # Simulate some mouse movement
            self._simulate_mouse_movement()
            
            return True
            
        except Exception as e:
            logging.error(f"Error navigating to FBR portal: {str(e)}")
            return False
    
    def verify_invoice(self, invoice_number):
        """
        Verify a single invoice number on the FBR portal.
        
        Args:
            invoice_number (str): The invoice number to verify
            
        Returns:
            str: Status - "Claimed", "Not Claimed", or "Error"
        """
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                # Navigate to FBR portal if not already there
                if self.driver.current_url != self.FBR_URL:
                    self.navigate_to_fbr()
                
                # Random delay to simulate human reading page
                self._random_delay(2.0, 4.0)
                
                # Simulate mouse movement before interacting
                self._simulate_mouse_movement()
                
                wait = WebDriverWait(self.driver, 15)
                
                try:
                    # Find the Invoice Ref No input field
                    # Try multiple selectors based on the FBR page structure
                    invoice_input = None
                    
                    # selectors_to_try = [
                    #     (By.XPATH, "//label[contains(text(), 'Invoice Ref No')]/following::input[1]"),
                    #     (By.XPATH, "//input[contains(@id, 'invoiceRefNo')]"),
                    #     (By.XPATH, "//input[contains(@name, 'invoiceRefNo')]"),
                    #     (By.XPATH, "//input[@type='text'][1]"),  # First text input as fallback
                    # ]
                    
                    selectors_to_try = [
                        # Exact id and name from the FBR page (most reliable)
                        (By.ID, "invoices_tabview:STform:invoiceNo"),
                        (By.NAME, "invoices_tabview:STform:invoiceNo"),
                        # Explicit XPaths for the same attributes as fallback
                        (By.XPATH, "//input[@id='invoices_tabview:STform:invoiceNo']"),
                        (By.XPATH, "//input[@name='invoices_tabview:STform:invoiceNo']"),
                        # Generic fallbacks (retain previous heuristics)
                        (By.XPATH, "//label[contains(text(), 'Invoice Ref No')]/following::input[1]"),
                        (By.XPATH, "//input[contains(@id, 'invoiceRefNo')]"),
                        (By.XPATH, "//input[contains(@name, 'invoiceRefNo')]"),
                        (By.XPATH, "//input[@type='text'][1]"),  # First text input as fallback
                    ]
                    for by_type, selector in selectors_to_try:
                        try:
                            invoice_input = wait.until(EC.presence_of_element_located((by_type, selector)))
                            logging.info(f"Found invoice input using selector: {selector}")
                            break
                        except TimeoutException:
                            continue
                    
                    if not invoice_input:
                        logging.error("Could not find invoice input field")
                        return "⚠️ Error - Field not found"
                    
                    # Human-like interaction: move to field and type naturally
                    self._human_like_click(invoice_input)
                    self._human_like_type(invoice_input, invoice_number)
                    logging.info(f"Entered invoice number: {invoice_number} (human-like typing)")
                    
                    # Random pause as if user is reviewing input
                    self._random_delay(0.8, 1.5)
                    
                    # Find and click the Search button
                    search_button = None
                    search_selectors = [
                        # Exact id and name from the button element
                        (By.ID, "invoices_tabview:STform:j_idt134"),
                        (By.NAME, "invoices_tabview:STform:j_idt134"),
                        (By.XPATH, "//button[@id='invoices_tabview:STform:j_idt134']"),
                        # Button that contains a span with the visible text "Search"
                        (By.XPATH, "//button[.//span[normalize-space(text())='Search']]"),
                        (By.XPATH, "//button[@type='submit' and .//span[contains(normalize-space(.),'Search')]]"),
                        # Generic fallbacks
                        (By.XPATH, "//button[contains(@class,'ui-button') and .//span[contains(normalize-space(.),'Search')]]"),
                        (By.XPATH, "//button[contains(normalize-space(.),'Search')]"),
                        (By.XPATH, "//input[@value='Search']"),
                        (By.XPATH, "//button[@type='submit']"),
                        (By.ID, "searchBtn"),
                    ]
                    
                    for by_type, selector in search_selectors:
                        try:
                            search_button = self.driver.find_element(by_type, selector)
                            logging.info(f"Found search button using: {selector}")
                            break
                        except NoSuchElementException:
                            continue
                    
                    if not search_button:
                        logging.error("Could not find search button")
                        return "⚠️ Error - Search button not found"
                    
                    # Human-like click on search button
                    self._human_like_click(search_button)
                    logging.info("Clicked search button (human-like)")
                    
                    # Random delay while "waiting" for results (appears more human)
                    self._random_delay(3.5, 5.0)
                    
                    # Check for results
                    page_source = self.driver.page_source.lower()
                    
                    # Check if "No records found" appears
                    if "no records found" in page_source or "no record found" in page_source:
                        logging.info(f"Invoice {invoice_number}: NOT CLAIMED (No records found)")
                        return "❌ Not Claimed"
                    
                    # Check if there are result rows in the table
                    try:
                        # Look for table rows with results (PrimeFaces table structure)
                        result_rows = self.driver.find_elements(By.XPATH, "//table//tr[contains(@class, 'ui-widget-content')]")
                        
                        if len(result_rows) > 0:
                            logging.info(f"Invoice {invoice_number}: CLAIMED (Found {len(result_rows)} result(s))")
                            return "✅ Claimed"
                        else:
                            # No rows found
                            logging.info(f"Invoice {invoice_number}: NOT CLAIMED (No table rows)")
                            return "❌ Not Claimed"
                    except:
                        # Fallback: check if invoice number appears in page
                        if str(invoice_number) in page_source:
                            logging.info(f"Invoice {invoice_number}: CLAIMED (Found in page)")
                            return "✅ Claimed"
                        else:
                            logging.info(f"Invoice {invoice_number}: NOT CLAIMED")
                            return "❌ Not Claimed"
                
                except TimeoutException:
                    logging.warning(f"Timeout while checking invoice {invoice_number} (Attempt {retry_count + 1})")
                    retry_count += 1
                    # Random retry delay
                    self._random_delay(2.0, 4.0)
                    
                except NoSuchElementException as e:
                    logging.warning(f"Element not found for invoice {invoice_number}: {str(e)} (Attempt {retry_count + 1})")
                    retry_count += 1
                    # Random retry delay
                    self._random_delay(2.0, 4.0)
                    
            except Exception as e:
                logging.error(f"Error verifying invoice {invoice_number}: {str(e)}")
                retry_count += 1
                # Random retry delay
                self._random_delay(2.0, 4.0)
        
        # If all retries failed
        logging.error(f"Failed to verify invoice {invoice_number} after {self.max_retries} attempts")
        return "⚠️ Error"
    
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
