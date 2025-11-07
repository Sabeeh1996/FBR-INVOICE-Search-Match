# 🧾 FBR Invoice Checker Bot

A complete Python automation tool with an interactive GUI that verifies invoice status on the Federal Board of Revenue (FBR) website using Selenium and Excel integration.

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## 📋 Features

✅ **Interactive GUI** - User-friendly Tkinter interface with real-time updates  
✅ **Excel Integration** - Read invoice numbers and write results automatically  
✅ **Web Automation** - Selenium-based FBR portal automation  
✅ **🎬 Macro Recording** - Record and replay custom workflows  
✅ **Live Progress Tracking** - Progress bar and statistics display  
✅ **Pause/Resume Support** - Control processing at any time  
✅ **Error Handling** - Automatic retry with detailed error logging  
✅ **Real-time Logs** - Scrolling log window with live updates  
✅ **Auto-save** - Results saved after each invoice verification  

---

## 🖥️ GUI Preview

```
-----------------------------------------
|   🧾  FBR Invoice Checker Bot          |
-----------------------------------------
| Excel File: [Browse...]               |
|---------------------------------------|
| 🎬 Macro: [Normal Mode] [Macro Mode]  |
| Select: [my_macro ▼] [⟳] [⏺][⏹]     |
|---------------------------------------|
| [Start] [Pause] [Resume] [Exit]       |
|---------------------------------------|
| Progress: [███████---------] 35%      |
| Total: 30 | Claimed: 15 | Not: 15     |
|---------------------------------------|
| Logs:                                 |
| Invoice #123456 → ✅ Claimed          |
| Invoice #123457 → ❌ Not Claimed      |
|---------------------------------------|
```

---

## 📁 Project Structure

```
FBR-INVOICE-STATUS-MATCHING/
├── main.py                  # Entry point - run this to start the app
├── gui.py                   # GUI layout and controls
├── excel_handler.py         # Excel read/write operations
├── fbr_checker.py          # Selenium automation for FBR
├── macro_recorder.py       # Macro recording and playback engine
├── create_sample_excel.py  # Generate sample Excel file
├── requirements.txt        # Python dependencies
├── invoices.xlsx          # Sample/actual invoice data
├── macros/                # Saved macro files
│   └── sample_fbr_check.json
├── logs/
│   ├── fbr_check_log.txt  # Detailed logs
│   └── screenshots/       # Error screenshots
├── MACRO_GUIDE.md         # Macro feature documentation
└── README.md              # This file
```

---

## 🚀 Installation

### Prerequisites

- **Python 3.10+** - [Download Python](https://www.python.org/downloads/)
- **Google Chrome** - [Download Chrome](https://www.google.com/chrome/)
- **Microsoft Excel** - To view/edit the invoice files

### Step 1: Clone or Download

```bash
cd c:\xampp\htdocs\FBR-INVOICE-STATUS-MATCHING
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `selenium` - Web automation
- `webdriver-manager` - Automatic ChromeDriver management
- `openpyxl` - Excel file operations

### Step 3: Verify Installation

```bash
python --version  # Should be 3.10 or higher
pip list | findstr selenium  # Verify selenium is installed
```

---

## 📊 Excel File Setup

### Required Format

Your Excel file must have:
- A column named **`InvoiceNumber`** (case-sensitive)
- Invoice numbers starting from row 2 (row 1 = headers)

### Example:

| InvoiceNumber   |
|-----------------|
| 1234567890123   |
| 2345678901234   |
| 3456789012345   |

### Create Sample File

```bash
python create_sample_excel.py
```

This creates `invoices.xlsx` with 10 sample invoice numbers.

---

## 🎯 Usage

### Method 1: Run with GUI (Recommended)

```bash
python main.py
```

**Steps:**
1. Application launches with welcome popup
2. Click **Browse** to select your Excel file
3. Choose **Normal Mode** or **Macro Mode**
   - Normal Mode: Built-in automation
   - Macro Mode: Use recorded workflows (see [Macro Guide](MACRO_GUIDE.md))
4. Click **Start** to begin verification
5. Chrome browser opens automatically
6. Watch progress and logs in real-time
7. Results are saved automatically to Excel
8. Summary popup appears when complete

### Method 2: Using Macros

For custom workflows, see the comprehensive **[Macro Recording Guide](MACRO_GUIDE.md)**.

Quick overview:
1. Click **⏺ Record** to start recording
2. Perform your workflow manually
3. Click **⏹ Stop** to save the macro
4. Switch to **Macro Mode** and select your macro
5. Process invoices using your recorded workflow

---

## ⚙️ Configuration

### FBR Website URL

The default FBR URL is set in `fbr_checker.py`:

```python
FBR_URL = "https://iris.fbr.gov.pk/customer/verification"
```

**To change:**
1. Open `fbr_checker.py`
2. Update the `FBR_URL` variable
3. Update element selectors in `verify_invoice()` method

### Element Selectors (IMPORTANT)

The web automation requires correct element selectors. You must configure these based on the actual FBR website:

**In `fbr_checker.py`, update these lines:**

```python
# Invoice input field (line ~95)
invoice_input = self.driver.find_element(By.ID, "invoiceNumber")

# Search button (line ~110)
search_button = self.driver.find_element(By.ID, "searchButton")

# Result container (line ~125)
result_element = self.driver.find_element(By.CLASS_NAME, "result")
```

**How to find correct selectors:**
1. Open FBR website in Chrome
2. Right-click on the invoice input field → **Inspect**
3. Note the element's `id`, `name`, or `class`
4. Update the code accordingly

---

## 🔍 How It Works

### Flow Diagram

```
1. User selects Excel file
        ↓
2. Read all invoice numbers from "InvoiceNumber" column
        ↓
3. Initialize Chrome browser with Selenium
        ↓
4. For each invoice:
   - Navigate to FBR portal
   - Enter invoice number
   - Click search
   - Scrape result
   - Determine status (Claimed/Not Claimed/Error)
   - Update Excel immediately
   - Update GUI progress
        ↓
5. Close browser
        ↓
6. Show completion summary
```

### Status Definitions

| Status | Meaning | Excel Output |
|--------|---------|--------------|
| ✅ Claimed | Invoice found and verified on FBR | `✅ Claimed` |
| ❌ Not Claimed | Invoice not found or unverified | `❌ Not Claimed` |
| ⚠️ Error | Network error or unable to verify | `⚠️ Error` |

---

## 📝 Output Format

After processing, your Excel file will have:

| InvoiceNumber | Status | Checked_On |
|---------------|--------|------------|
| 1234567890123 | ✅ Claimed | 2025-10-26 10:45:23 AM |
| 2345678901234 | ❌ Not Claimed | 2025-10-26 10:47:15 AM |
| 3456789012345 | ⚠️ Error | 2025-10-26 10:49:02 AM |

---

## 🐛 Troubleshooting

### Issue: ChromeDriver not found

**Solution:**
- Ensure Google Chrome is installed
- Run: `pip install --upgrade webdriver-manager`
- The tool will auto-download the correct ChromeDriver

### Issue: "InvoiceNumber column not found"

**Solution:**
- Open your Excel file
- Ensure column header is exactly `InvoiceNumber` (case-sensitive)
- No extra spaces or special characters

### Issue: Browser opens but doesn't interact with page

**Solution:**
- The element selectors need updating
- Follow the "Element Selectors" configuration section above
- Inspect the FBR website and update `fbr_checker.py`

### Issue: All results show "Error"

**Solution:**
- Check internet connection
- Verify FBR website is accessible
- Update `FBR_URL` if the site has changed
- Check element selectors are correct

### Issue: "Access Denied" or CAPTCHA

**Solution:**
- FBR may have bot detection
- Add delays: increase `time.sleep()` values in `fbr_checker.py`
- Consider manual verification for CAPTCHAs
- Use residential proxy if needed (advanced)

---

## 📄 Logging

All activities are logged to `logs/fbr_check_log.txt`:

```
2025-10-26 10:45:00 - INFO - FBR Invoice Checker Bot Started
2025-10-26 10:45:05 - INFO - Excel file loaded successfully
2025-10-26 10:45:10 - INFO - Chrome browser initialized
2025-10-26 10:45:15 - INFO - Invoice 1234567890123: CLAIMED
2025-10-26 10:45:20 - INFO - Invoice 2345678901234: NOT CLAIMED
```

---

## 🔒 Security & Privacy

- No data is sent to external servers (except FBR for verification)
- All processing happens locally on your machine
- Credentials (if needed) should be stored in `.env` file
- Never commit `.env` or `invoices.xlsx` to public repositories

---

## 🧩 Advanced Usage

### Macro Recording & Playback

The bot now supports macro recording for complex workflows. See **[MACRO_GUIDE.md](MACRO_GUIDE.md)** for:
- Recording custom workflows
- Editing macro JSON files
- Using template variables
- Sharing macros with team members
- Advanced error handling
- Troubleshooting macro issues

### Running Headless (No Browser Window)

In `fbr_checker.py`, add to `initialize_browser()`:

```python
chrome_options.add_argument('--headless')
```

### Adding Proxy Support

```python
chrome_options.add_argument('--proxy-server=http://your-proxy:port')
```

### Scheduling Automated Runs

Use Windows Task Scheduler:
1. Create a batch file: `run_fbr_checker.bat`
```batch
@echo off
cd c:\xampp\htdocs\FBR-INVOICE-STATUS-MATCHING
python main.py
```
2. Schedule it via Task Scheduler

---

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push and create a Pull Request

---

## 📞 Support

For issues or questions:
- Check the Troubleshooting section
- Review logs in `logs/fbr_check_log.txt`
- Open an issue on GitHub

---

## 📜 License

MIT License - Feel free to use and modify for your needs.

---

## ⚠️ Disclaimer

This tool is for legitimate invoice verification purposes only. Users are responsible for:
- Complying with FBR terms of service
- Not overloading FBR servers
- Ensuring data accuracy
- Following local regulations

The developers are not responsible for misuse or any consequences of using this tool.

---

## 🎉 Quick Start Summary

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Create sample Excel (or use your own)
python create_sample_excel.py

# 3. Run the application
python main.py

# 4. Select Excel file → Start → Done!
```

---

**Made with ❤️ for FBR invoice verification automation**

Last Updated: October 26, 2025
#   F B R - I N V O I C E - S e a r c h - M a t c h 
 
 