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
            # Ensure element is in view first
            try:
                self.driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'auto', block: 'center', inline: 'center'});",
                    element,
                )
            except Exception:
                # ignore scroll failures
                pass

            self._random_delay(0.2, 0.6)

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
                self._random_delay(0.15, 0.4)
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
                    'formatted': parsed_date.strftime('%d-%b-%Y')  # Format: 11-Nov-2025
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
                    # Try to find the element with shorter timeout for faster fallback
                    claim_button = WebDriverWait(self.driver, 3).until(
                        EC.presence_of_element_located((by_type, selector))
                    )
                    
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
            self._random_delay(0.5, 1.0)
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
            self._random_delay(1.0, 2.0)
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
                WebDriverWait(self.driver, 15).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                logging.info("✓ Page fully loaded")
            except TimeoutException:
                logging.warning("Page load timeout, but proceeding anyway...")
            
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
            
            # Random delay to simulate page reading
            self._random_delay(2.0, 4.0)
            
            # Simulate some mouse movement
            self._simulate_mouse_movement()
            
            return True
            
        except WebDriverException as e:
            logging.error(f"Browser closed or connection lost: {str(e)}")
            return False
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
        try:
            # Check if browser is still alive before proceeding
            if not self.is_browser_alive():
                logging.error("Browser was closed by user")
                return {
                    'status': '⚠️ Browser Closed',
                    'value_of_purchases': 'N/A'
                }
            
            # Process the claim workflow (Annex-A steps)
            self._random_delay(0.5, 1.0)
            self.process_claim_workflow()
            
            # Random delay to simulate human reading page
            self._random_delay(0.5, 1.0)
            
            # Simulate mouse movement before interacting
            self._simulate_mouse_movement()
            
            # Wait for page to fully load
            logging.info("Waiting for page to fully load...")
            try:
                WebDriverWait(self.driver, 60).until(
                    lambda driver: driver.execute_script("return document.readyState") == "complete"
                )
                logging.info("✓ Page fully loaded")
            except TimeoutException:
                logging.warning("Page load timeout, but proceeding anyway...")
            
            wait = WebDriverWait(self.driver, 60)
            
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
                        self._random_delay(0.5, 1.0)
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
                self._random_delay(0.3, 0.5)
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
                self._random_delay(0.3, 0.5)
                
                # Verify the value was entered
                entered_value = seller_ntn_input.get_attribute('value')
                if entered_value != str(invoice_number):
                    logging.error(f"STEP 2 VERIFICATION FAILED: Expected '{invoice_number}', got '{entered_value}'")
                    return {
                        'status': '⚠️ Error - NTN entry verification failed',
                        'value_of_purchases': 'N/A'
                    }
                
                logging.info(f"✓ STEP 2 COMPLETED & VERIFIED: Seller NTN = '{entered_value}'")
                self._random_delay(0.5, 1.0)
            
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
                self._random_delay(0.3, 0.5)
                
                # Verify the value was entered
                entered_value = invoice_no_input.get_attribute('value')
                if entered_value != str(invoice_no_field):
                    logging.error(f"STEP 3 VERIFICATION FAILED: Expected '{invoice_no_field}', got '{entered_value}'")
                    return {
                        'status': '⚠️ Error - Invoice entry verification failed',
                        'value_of_purchases': 'N/A'
                    }
                
                logging.info(f"✓ STEP 3 COMPLETED & VERIFIED: Invoice Number = '{entered_value}'")
                self._random_delay(0.5, 1.0)
            
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
                self._random_delay(0.3, 0.5)
                
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
                self._random_delay(0.3, 0.5)
                
                # Verify To Date was set
                to_date_value = to_date_input.get_attribute('value')
                if to_date_value != date_formatted:
                    logging.error(f"STEP 4 TO DATE VERIFICATION FAILED: Expected '{date_formatted}', got '{to_date_value}'")
                    return {
                        'status': '⚠️ Error - To Date verification failed',
                        'value_of_purchases': 'N/A'
                    }
                
                logging.info(f"✓ STEP 4 COMPLETED & VERIFIED: Dates set to '{date_formatted}'")
                self._random_delay(0.5, 1.0)
            
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
                self._random_delay(0.5, 1.0)
                
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
            self._random_delay(0.5, 1.0)
            
            # Step 6: Click the checkbox in the results table if results found
            logging.info("STEP 6: Looking for checkbox in results table...")
            try:
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
                
                # Multiple selector strategies for the checkbox with dynamic ID support
                checkbox_selectors = [
                    # Strategy 1: Partial ID match - purchaseInvoiceTable with dynamic j_idt
                    (By.XPATH, "//div[contains(@id, 'purchaseInvoiceTable:j_idt')]//div[contains(@class, 'ui-chkbox-box')]"),
                    
                    # Strategy 2: First checkbox with ui-chkbox class in the table
                    (By.XPATH, "//table[contains(@id, 'purchaseInvoiceTable')]//div[contains(@class, 'ui-chkbox')]"),
                    
                    # Strategy 3: Checkbox input within table row (first row)
                    (By.XPATH, "//table[contains(@id, 'purchaseInvoiceTable')]//tbody//tr[1]//div[contains(@class, 'ui-chkbox-box')]"),
                    
                    # Strategy 4: Any checkbox div with ui-chkbox-box in table context
                    (By.XPATH, "//div[contains(@id, 'purchaseInvoiceTable')]//div[contains(@class, 'ui-chkbox-box')]"),
                    
                    # Strategy 5: Checkbox with input element inside table
                    (By.XPATH, "//table[contains(@id, 'purchaseInvoiceTable')]//input[contains(@id, 'j_idt') and @type='checkbox']/preceding-sibling::div[contains(@class, 'ui-chkbox-box')]"),
                    
                    # Strategy 6: Generic - first visible checkbox in table
                    (By.XPATH, "//table[contains(@id, 'purchaseInvoiceTable')]//div[contains(@class, 'ui-chkbox-box')][1]"),
                    
                    # Strategy 7: CSS selector with partial attribute matching
                    (By.CSS_SELECTOR, "div[id*='purchaseInvoiceTable'][id*='j_idt'] .ui-chkbox-box"),
                    
                    # Strategy 8: Checkbox in loadAnnexAform table context
                    (By.XPATH, "//form[contains(@id, 'loadAnnexAform')]//table[contains(@id, 'purchaseInvoiceTable')]//div[contains(@class, 'ui-chkbox-box')]"),
                ]
                
                checkbox_element = None
                for by_type, selector in checkbox_selectors:
                    try:
                        # Try to find the element with shorter timeout for faster fallback
                        checkbox_element = checkbox_wait.until(EC.visibility_of_element_located((by_type, selector)))
                        
                        # Verify element is actually clickable
                        checkbox_element = checkbox_wait.until(EC.element_to_be_clickable((by_type, selector)))
                        logging.info(f"✓ Found checkbox using selector: {selector}")
                        break
                        
                    except (TimeoutException, NoSuchElementException) as e:
                        logging.debug(f"Selector failed: {selector} - {type(e).__name__}")
                        continue
                    except Exception as e:
                        logging.debug(f"Unexpected error with selector {selector}: {str(e)}")
                        continue
                
                # Fallback: Use JavaScript to find checkbox if all selectors fail
                if not checkbox_element:
                    logging.warning("All selectors failed, trying JavaScript fallback...")
                    try:
                        checkbox_element = self.driver.execute_script("""
                            // Find the purchase invoice table
                            var table = document.querySelector('table[id*="purchaseInvoiceTable"]');
                            if (!table) return null;
                            
                            // Find first checkbox in the table
                            var checkboxDiv = table.querySelector('div[class*="ui-chkbox-box"]');
                            if (checkboxDiv && checkboxDiv.offsetParent !== null) {
                                return checkboxDiv;
                            }
                            
                            // Alternative: Find input checkbox and its wrapper
                            var checkboxInput = table.querySelector('input[type="checkbox"]');
                            if (checkboxInput) {
                                var wrapper = checkboxInput.closest('div[class*="ui-chkbox"]');
                                if (wrapper) {
                                    var checkBox = wrapper.querySelector('div[class*="ui-chkbox-box"]');
                                    if (checkBox && checkBox.offsetParent !== null) {
                                        return checkBox;
                                    }
                                }
                            }
                            
                            // Last resort: Find any visible checkbox element
                            var allCheckboxes = table.querySelectorAll('div[class*="ui-chkbox-box"]');
                            for (var i = 0; i < allCheckboxes.length; i++) {
                                if (allCheckboxes[i].offsetParent !== null) {
                                    return allCheckboxes[i];
                                }
                            }
                            
                            return null;
                        """)
                        
                        if checkbox_element:
                            logging.info("✓ Found checkbox using JavaScript fallback")
                        
                    except Exception as js_error:
                        logging.error(f"JavaScript fallback also failed: {str(js_error)}")
                
                if not checkbox_element:
                    logging.error("STEP 6 FAILED: Checkbox not found in results table after trying all strategies")
                    return {
                        'status': '⚠️ No results',
                        'value_of_purchases': 'N/A'
                    }
                
                # Human-like click on the checkbox
                self._human_like_click(checkbox_element)
                self._random_delay(0.5, 1.0)
                
                # Verify checkbox was clicked by checking its state
                checkbox_checked = self.driver.execute_script("""
                    var checkbox = document.querySelector('#correspondenceTabs\\\\:loadAnnexAform\\\\:purchaseInvoiceTable\\\\:j_idt5893_input');
                    return checkbox ? checkbox.checked : false;
                """)
                
                if not checkbox_checked:
                    logging.warning("STEP 6: Checkbox state not confirmed as checked, but proceeding...")
                
                logging.info("✓ STEP 6 COMPLETED: Checkbox clicked in results table")
                self._random_delay(0.5, 1.0)
                
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
                self._random_delay(0.5, 1.0)
                
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
                    self._random_delay(0.5, 1.5)
                    
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
                
                # Final verification: Ensure button text is exactly "Claim"
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
                self._random_delay(1.0, 2.0)
                
                ####################################################################################

                # Step 9: Wait for success message
                logging.info("STEP 9: Waiting for 'Purchase Invoice(s) loaded Successfully' message...")
                
                success_message_found = False
                success_wait = WebDriverWait(self.driver, 60)
                
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
                
                # Return both status and the value
                return {
                    'status': final_status,
                    'value_of_purchases': value_of_purchases
                }
                
            except TimeoutException:
                logging.error("STEP 6/7 FAILED: Timeout exception")
                return {
                    'status': '⚠️ Error - Timeout',
                    'value_of_purchases': 'N/A'
                }
            except WebDriverException as e:
                logging.error(f"STEP 6/7 FAILED: Browser closed or disconnected: {str(e)}")
                return {
                    'status': '⚠️ Browser Closed',
                    'value_of_purchases': 'N/A'
                }
            except Exception as e:
                logging.error(f"STEP 6/7 FAILED: {str(e)}")
                return {
                    'status': '⚠️ Error',
                    'value_of_purchases': 'N/A'
                }
            
        except WebDriverException as e:
            logging.error(f"Browser closed by user during verification: {str(e)}")
            return {
                'status': '⚠️ Browser Closed',
                'value_of_purchases': 'N/A'
            }
        except Exception as e:
            logging.error(f"Error verifying invoice {invoice_number}: {str(e)}")
            return {
                'status': '⚠️ Error',
                'value_of_purchases': 'N/A'
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
