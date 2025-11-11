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
    
    def _select_date_from_datepicker(self, date_string):
        """
        Parse date string and select date from datepicker calendar.
        
        Args:
            date_string: Date in format like '07-Apr-2025' or similar
            
        Returns:
            dict: Parsed date with 'day', 'month', 'year' keys, or None if parsing failed
        """
        try:
            from datetime import datetime
            
            # Try multiple date formats
            date_formats = [
                '%d-%b-%Y',      # 07-Apr-2025
                '%d-%B-%Y',      # 07-April-2025
                '%Y-%m-%d',      # 2025-04-07
                '%d/%m/%Y',      # 07/04/2025
                '%m/%d/%Y',      # 04/07/2025
            ]
            
            parsed_date = None
            for date_format in date_formats:
                try:
                    parsed_date = datetime.strptime(str(date_string), date_format)
                    break
                except ValueError:
                    continue
            
            if parsed_date:
                return {
                    'day': parsed_date.day,
                    'month': parsed_date.month,
                    'year': parsed_date.year,
                    'formatted': parsed_date.strftime('%d/%m/%Y')
                }
            else:
                logging.warning(f"Could not parse date: {date_string}")
                return None
                
        except Exception as e:
            logging.error(f"Error parsing date {date_string}: {str(e)}")
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
            self._random_delay(1.5, 2.5)
            logging.info("✅ Clicked Annex-A (Purchases) tab")
            return True
            
        except Exception as e:
            logging.warning(f"Error clicking Annex-A tab: {str(e)}")
            return False
    
    def click_claim_invoices_button(self):
        """
        Click the 'Claim Invoices' dropdown button after Annex-A tab is active.
        
        Returns:
            bool: True if button was found and clicked, False otherwise
        """
        try:
            # Look for the span with ui-menubutton class containing the button
            claim_button = None
            selectors = [
                # Exact ID from the provided HTML
                (By.ID, "correspondenceTabs:annexa-form:j_idt6954_button"),
                (By.XPATH, "//button[contains(@id, 'annexa-form:j_idt6954_button')]"),
                (By.XPATH, "//span[@class='ui-menubutton']//button[contains(normalize-space(.), 'Claim Invoices')]"),
                (By.XPATH, "//button[contains(@class, 'ui-menubutton') or ancestor::span[@class='ui-menubutton']]//span[contains(text(), 'Claim Invoices')]"),
                (By.XPATH, "//button[.//span[contains(text(), 'Claim Invoices')]]"),
            ]
            
            for by_type, selector in selectors:
                try:
                    claim_button = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((by_type, selector))
                    )
                    logging.info(f"Found Claim Invoices button using selector: {selector}")
                    break
                except TimeoutException:
                    continue
            
            if not claim_button:
                logging.error("Claim Invoices button not found")
                return False
            
            # Click the button
            self._human_like_click(claim_button)
            self._random_delay(1.0, 2.0)
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
            self._random_delay(2.0, 3.5)
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
            
            # Step 1: Click Annex-A tab
            if not self.click_annex_a_tab():
                logging.warning("Annex-A tab workflow skipped (tab not found)")
                return False
            
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
        
    def verify_invoice(self, invoice_number, source_authority=None, invoice_no_field=None, date_field=None):
        """
        Verify a single invoice number on the FBR portal.
        
        Args:
            invoice_number (str): The seller registration number (NTN) to verify
            source_authority (str): Source Authority value (e.g., 'FBR', 'BRA', 'KPRA', 'PRA', 'SRB')
            invoice_no_field (str): Invoice number from 'Number' column in Excel
            date_field (str): Date from 'Date' column in Excel (will be used for both From and To dates)
            
        Returns:
            str: Status - "Claimed", "Not Claimed", or "Error"
        """
         # Now process the claim workflow (Annex-A steps)
        self._random_delay(1.0, 2.0)
        self.process_claim_workflow()
        retry_count = 0
        
        while retry_count < self.max_retries:
            try:
                # Navigate to FBR portal if not already there
               # if self.driver.current_url != self.FBR_URL:
                #    self.navigate_to_fbr()
                
                # Random delay to simulate human reading page
                self._random_delay(2.0, 4.0)
                
                # Simulate mouse movement before interacting
                self._simulate_mouse_movement()
                
                wait = WebDriverWait(self.driver, 15)
                
                try:
                    # Step 1: Select Source Authority from dropdown if provided
                    if source_authority:
                        logging.info(f"Selecting Source Authority: {source_authority}")
                        
                        # Find the dropdown element
                        dropdown_selectors = [
                            (By.ID, "correspondenceTabs:loadAnnexAform:sourceAuthorityFilter"),
                            (By.XPATH, "//div[@id='correspondenceTabs:loadAnnexAform:sourceAuthorityFilter']"),
                            (By.XPATH, "//div[contains(@class, 'ui-selectonemenu') and contains(@id, 'sourceAuthorityFilter')]"),
                        ]
                        
                        dropdown = None
                        for by_type, selector in dropdown_selectors:
                            try:
                                dropdown = wait.until(EC.presence_of_element_located((by_type, selector)))
                                logging.info(f"Found dropdown using selector: {selector}")
                                break
                            except TimeoutException:
                                continue
                        
                        if dropdown:
                            # Click the dropdown to open it
                            self._human_like_click(dropdown)
                            self._random_delay(0.5, 1.0)
                            
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
                            
                            if option_value:
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
                                        logging.info(f"✓ Selected Source Authority: {source_auth_normalized}")
                                        option_selected = True
                                        self._random_delay(0.5, 1.0)
                                        break
                                    except TimeoutException:
                                        continue
                                
                                if not option_selected:
                                    logging.warning(f"Could not select option '{source_auth_normalized}' from dropdown, proceeding anyway")
                            else:
                                logging.warning(f"Unknown source authority '{source_authority}', valid values: {list(authority_map.keys())}")
                        else:
                            logging.warning("Source Authority dropdown not found, proceeding without selection")
                    
                    # Step 2: Enter Seller NTN in the annexASellerRegNo field
                    if invoice_number:
                        logging.info(f"Entering Seller NTN: {invoice_number}")
                        
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
                                seller_ntn_input = wait.until(EC.presence_of_element_located((by_type, selector)))
                                logging.info(f"Found Seller NTN input using selector: {selector}")
                                break
                            except TimeoutException:
                                continue
                        
                        if seller_ntn_input:
                            # Human-like interaction: move to field and type naturally
                            self._human_like_click(seller_ntn_input)
                            self._human_like_type(seller_ntn_input, invoice_number)
                            logging.info(f"✓ Entered Seller NTN: {invoice_number}")
                            self._random_delay(0.8, 1.5)
                        else:
                            logging.warning("Seller NTN input field not found, skipping this step")
                    
                    # Step 3: Enter Invoice Number in the annexAinvoiceNoId field
                    if invoice_no_field:
                        logging.info(f"Entering Invoice Number: {invoice_no_field}")
                        
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
                                invoice_no_input = wait.until(EC.presence_of_element_located((by_type, selector)))
                                logging.info(f"Found Invoice Number input using selector: {selector}")
                                break
                            except TimeoutException:
                                continue
                        
                        if invoice_no_input:
                            # Human-like interaction: move to field and type naturally
                            self._human_like_click(invoice_no_input)
                            self._human_like_type(invoice_no_input, invoice_no_field)
                            logging.info(f"✓ Entered Invoice Number: {invoice_no_field}")
                            self._random_delay(0.8, 1.5)
                        else:
                            logging.warning("Invoice Number input field not found, skipping this step")
                    
                    # Step 4: Select From Date and To Date from datepickers
                    if date_field and date_field != 'N/A':
                        logging.info(f"Selecting dates: {date_field}")
                        
                        # Parse the date
                        parsed_date = self._select_date_from_datepicker(date_field)
                        
                        if parsed_date:
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
                                    from_date_input = wait.until(EC.presence_of_element_located((by_type, selector)))
                                    logging.info(f"Found From Date input using selector: {selector}")
                                    break
                                except TimeoutException:
                                    continue
                            
                            if from_date_input:
                                # Click to open datepicker, then use JavaScript to set value directly
                                # (readonly fields require JS to set value)
                                self.driver.execute_script(f"arguments[0].value = '{date_formatted}';", from_date_input)
                                logging.info(f"✓ Set From Date: {date_formatted}")
                                self._random_delay(0.5, 1.0)
                            else:
                                logging.warning("From Date input field not found")
                            
                            # Select To Date (same date)
                            to_date_selectors = [
                                (By.ID, "correspondenceTabs:loadAnnexAform:annexAToDate_input"),
                                (By.NAME, "correspondenceTabs:loadAnnexAform:annexAToDate_input"),
                                (By.XPATH, "//input[@id='correspondenceTabs:loadAnnexAform:annexAToDate_input']"),
                            ]
                            
                            to_date_input = None
                            for by_type, selector in to_date_selectors:
                                try:
                                    to_date_input = wait.until(EC.presence_of_element_located((by_type, selector)))
                                    logging.info(f"Found To Date input using selector: {selector}")
                                    break
                                except TimeoutException:
                                    continue
                            
                            if to_date_input:
                                # Use JavaScript to set value directly
                                self.driver.execute_script(f"arguments[0].value = '{date_formatted}';", to_date_input)
                                logging.info(f"✓ Set To Date: {date_formatted}")
                                self._random_delay(0.5, 1.0)
                            else:
                                logging.warning("To Date input field not found")
                        else:
                            logging.warning(f"Could not parse date: {date_field}")
                    
                    # Step 5: Enter invoice number in the Seller Registration No. field
                    invoice_input = None
                    
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
                            
                            # Now process the claim workflow (Annex-A steps)
                           
                            
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
