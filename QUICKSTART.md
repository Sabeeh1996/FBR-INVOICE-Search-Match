# 🚀 Quick Start Guide

## For First-Time Users

### Step 1: Install Python Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Prepare Your Excel File

**Option A: Use sample file**
```bash
python create_sample_excel.py
```

**Option B: Use your own file**
- Create Excel file with column named `InvoiceNumber`
- Add your invoice numbers starting from row 2

### Step 3: Configure FBR Selectors (CRITICAL)

⚠️ **You MUST update element selectors in `fbr_checker.py` to match the actual FBR website**

1. Open FBR invoice verification page in Chrome
2. Right-click invoice input field → Inspect
3. Note the element ID/name/class
4. Update these lines in `fbr_checker.py`:
   - Line ~95: Invoice input field selector
   - Line ~110: Search button selector  
   - Line ~125: Result container selector

Example:
```python
# If FBR input has id="txtInvoice"
invoice_input = self.driver.find_element(By.ID, "txtInvoice")

# If button has class="btn-search"
search_button = self.driver.find_element(By.CLASS_NAME, "btn-search")
```

### Step 4: Run the Application
```bash
python main.py
```

### Step 5: Use the GUI
1. Click **Browse** → Select your Excel file
2. Click **Start** → Browser opens automatically
3. Watch progress in real-time
4. Results save automatically
5. View summary when complete

---

## Common First-Run Issues

### 1. ChromeDriver Error
**Solution:** Ensure Chrome browser is installed
```bash
pip install --upgrade webdriver-manager
```

### 2. Element Not Found Error
**Solution:** Update selectors in `fbr_checker.py` (see Step 3 above)

### 3. Excel Column Error
**Solution:** Column must be named exactly `InvoiceNumber`

---

## Testing Without FBR

To test the GUI without actually connecting to FBR:

1. Comment out the browser automation in `gui.py`
2. Use mock data for testing
3. Or manually verify the Excel file structure works

---

## Next Steps

- Read full documentation in `README.md`
- Check logs in `logs/fbr_check_log.txt`
- Customize delays in `fbr_checker.py` if needed
- Add your own invoice numbers to `invoices.xlsx`

---

**Need Help?** Check the Troubleshooting section in README.md
