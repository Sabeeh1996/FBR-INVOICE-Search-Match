"""
FBR Checker Module
Handles web automation for checking invoice status on FBR website using Selenium.
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
import logging
import time


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
        
    def initialize_browser(self):
        """
        Initialize Chrome browser with appropriate options.
        
        Returns:
            bool: True if browser initialized successfully, False otherwise
        """
        try:
            # Chrome options for better stability
            chrome_options = webdriver.ChromeOptions()
            chrome_options.add_argument('--start-maximized')
            chrome_options.add_argument('--disable-blink-features=AutomationControlled')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Fix SSL handshake errors
            chrome_options.add_argument('--ignore-certificate-errors')
            chrome_options.add_argument('--ignore-ssl-errors')
            chrome_options.add_argument('--allow-insecure-localhost')
            chrome_options.add_argument('--disable-web-security')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            # Suppress console logging
            chrome_options.add_argument('--log-level=3')
            chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            
            # Initialize Chrome driver with auto-install using webdriver-manager
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            # Set implicit wait
            self.driver.implicitly_wait(10)
            
            logging.info("Chrome browser initialized successfully")
            return True
            
        except WebDriverException as e:
            logging.error(f"Failed to initialize Chrome browser: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error initializing browser: {str(e)}")
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
            time.sleep(2)  # Wait for page to load
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
                
                # Wait for page to fully load
                time.sleep(3)
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
                    
                    # Clear and enter invoice number
                    invoice_input.clear()
                    time.sleep(0.5)
                    invoice_input.send_keys(str(invoice_number))
                    logging.info(f"Entered invoice number: {invoice_number}")
                    time.sleep(1)
                    
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
                    
                    search_button.click()
                    logging.info("Clicked search button")
                    
                    # Wait for results to load
                    time.sleep(4)
                    
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
                    time.sleep(2)
                    
                except NoSuchElementException as e:
                    logging.warning(f"Element not found for invoice {invoice_number}: {str(e)} (Attempt {retry_count + 1})")
                    retry_count += 1
                    time.sleep(2)
                    
            except Exception as e:
                logging.error(f"Error verifying invoice {invoice_number}: {str(e)}")
                retry_count += 1
                time.sleep(2)
        
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
