# FBR Website Configuration Guide

## 🎯 Purpose
This guide helps you configure the correct element selectors for the FBR invoice verification website.

---

## 📍 Step-by-Step Configuration

### Step 1: Open FBR Website
1. Open Chrome browser
2. Navigate to: `https://iris.fbr.gov.pk/customer/verification`
   (or your specific FBR invoice verification URL)

### Step 2: Inspect Invoice Input Field
1. Right-click on the invoice number input box
2. Select **"Inspect"** or press `F12`
3. The Developer Tools will open
4. Look for the HTML element (it will be highlighted)

Example:
```html
<input type="text" id="invoiceNo" name="invoice" class="form-control">
```

**What to note:**
- `id="invoiceNo"` → Use: `By.ID, "invoiceNo"`
- `name="invoice"` → Use: `By.NAME, "invoice"`
- `class="form-control"` → Use: `By.CLASS_NAME, "form-control"`

### Step 3: Inspect Search/Verify Button
1. Right-click on the search or verify button
2. Select **"Inspect"**
3. Note the button's attributes

Example:
```html
<button type="submit" id="btnSearch" class="btn btn-primary">Verify</button>
```

### Step 4: Inspect Result Container
1. After submitting a test invoice, inspect the result area
2. Look for the container that shows "Claimed" or "Not Found"

Example:
```html
<div id="resultContainer" class="alert alert-success">
  Invoice Claimed Successfully
</div>
```

---

## 🔧 Update fbr_checker.py

Open `fbr_checker.py` and find the `verify_invoice()` method.

### Update Line ~95 (Invoice Input Field)

**Before:**
```python
invoice_input = WebDriverWait(self.driver, 10).until(
    EC.presence_of_element_located((By.ID, "invoiceNumber"))
)
```

**After (example with actual FBR ID):**
```python
invoice_input = WebDriverWait(self.driver, 10).until(
    EC.presence_of_element_located((By.ID, "txtInvoiceNo"))  # Use actual ID
)
```

### Update Line ~110 (Search Button)

**Before:**
```python
search_button = self.driver.find_element(By.ID, "searchButton")
```

**After (example):**
```python
search_button = self.driver.find_element(By.ID, "btnVerify")  # Use actual ID
```

### Update Line ~125 (Result Container)

**Before:**
```python
result_element = WebDriverWait(self.driver, 10).until(
    EC.presence_of_element_located((By.CLASS_NAME, "result"))
)
```

**After (example):**
```python
result_element = WebDriverWait(self.driver, 10).until(
    EC.presence_of_element_located((By.ID, "divResult"))  # Use actual ID
)
```

---

## 📋 Selector Types Cheat Sheet

### By ID (Most Reliable)
```python
element = driver.find_element(By.ID, "elementId")
```

### By NAME
```python
element = driver.find_element(By.NAME, "elementName")
```

### By CLASS
```python
element = driver.find_element(By.CLASS_NAME, "className")
```

### By XPATH (Most Flexible)
```python
element = driver.find_element(By.XPATH, "//input[@type='text']")
```

### By CSS Selector
```python
element = driver.find_element(By.CSS_SELECTOR, "input.form-control")
```

---

## 🧪 Testing Your Configuration

### Method 1: Manual Test
1. Run `python main.py`
2. Select Excel file with 1-2 test invoices
3. Click Start
4. Watch the browser and check if:
   - Invoice number is entered correctly
   - Search button is clicked
   - Result is captured

### Method 2: Browser Console Test
1. Open FBR site
2. Press F12 → Console tab
3. Test selectors:
```javascript
// Test if element exists
document.getElementById("invoiceNo")
document.querySelector(".result")
```

---

## 🚨 Common Issues

### Issue 1: Element Not Found
**Cause:** Incorrect selector or element loads after page load  
**Solution:** Use `WebDriverWait` with explicit wait

```python
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

element = WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "yourElementId"))
)
```

### Issue 2: Multiple Elements Match
**Cause:** Class name is not unique  
**Solution:** Use more specific selector like ID or XPATH

```python
# Instead of class
element = driver.find_element(By.CLASS_NAME, "input")

# Use XPATH with multiple conditions
element = driver.find_element(By.XPATH, "//input[@type='text' and @name='invoice']")
```

### Issue 3: Dynamic IDs
**Cause:** Element IDs change on each page load  
**Solution:** Use XPATH with contains or starts-with

```python
element = driver.find_element(By.XPATH, "//input[contains(@id, 'invoice')]")
```

---

## 📸 Screenshot Debugging

Add this to `fbr_checker.py` for debugging:

```python
def verify_invoice(self, invoice_number):
    try:
        # ... your code ...
        
        # Take screenshot for debugging
        self.driver.save_screenshot(f"debug_{invoice_number}.png")
        
        # ... rest of code ...
```

---

## ✅ Validation Checklist

Before running on large dataset:

- [ ] FBR URL is correct in `FBR_URL` variable
- [ ] Invoice input field selector works
- [ ] Search button selector works
- [ ] Result container selector works
- [ ] Result text contains keywords: "claimed", "verified", "not found"
- [ ] Tested with 2-3 sample invoices manually
- [ ] Screenshots show correct element interaction
- [ ] No CAPTCHA blocking automation

---

## 🔗 Useful Resources

- [Selenium Documentation](https://selenium-python.readthedocs.io/)
- [XPath Syntax Guide](https://www.w3schools.com/xml/xpath_syntax.asp)
- [CSS Selector Reference](https://www.w3schools.com/cssref/css_selectors.asp)

---

## 💡 Pro Tips

1. **Use Browser DevTools Network Tab** to see AJAX requests
2. **Check for iframes** - FBR might use iframes for the form
3. **Add delays** - Some sites need time to load elements
4. **Handle popups** - Close any modal dialogs before interacting
5. **Check for redirects** - Site might redirect after verification

---

**Last Updated:** October 26, 2025  
**Tested With:** Selenium 4.15.2, Chrome 118+
