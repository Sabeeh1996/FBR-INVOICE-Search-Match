# Sales Tax/FED in ST Mode Matching Implementation

## Overview
Enhanced the FBR Invoice Status Matching system to match rows in the FBR results table based on the "Sales Tax/FED in ST Mode" column from the Excel sheet. Only the matching row will have its checkbox clicked.

## Changes Made

### 1. **fbr_checker.py**

#### Method Signature Update
```python
def verify_invoice(self, invoice_number, source_authority=None, invoice_no_field=None, 
                   date_field=None, sales_tax_fed_st_mode=None):
```

**New Parameter:**
- `sales_tax_fed_st_mode` (str): Sales Tax/FED in ST Mode value from Excel to match with FBR data

#### Step 6 Logic Enhancement
Changed the checkbox selection logic from "always click first checkbox" to:

1. **If `sales_tax_fed_st_mode` is provided:**
   - Extract all table rows and their data using JavaScript
   - Find the "Sales Tax/ FED in ST Mode" column header
   - Iterate through all rows and find the one matching the provided value
   - Click the checkbox ONLY for that matching row

2. **If `sales_tax_fed_st_mode` is NOT provided:**
   - Falls back to original behavior (click first available checkbox)

#### Key Features of the Matching Algorithm:
- **Case-insensitive column header search**: Finds "Sales Tax/ FED in ST Mode" even if column names vary slightly
- **Comma and space-insensitive value comparison**: Compares values like "50,000" with "50000" as equal
- **Fallback mechanisms**: If matching fails, falls back to first checkbox
- **Comprehensive logging**: Logs all matching attempts and results for debugging

### 2. **excel_handler.py**

#### Extended Column Support
Added to the `column_names` list:
```python
'purchase type',
'rate',
'value of purchases',
'sales tax/ fed in st mode'
```

#### Enhanced `get_invoice_numbers()` Method
Added extraction of the "Sales Tax/FED in ST Mode" field:
```python
if 'sales tax/ fed in st mode' in self.column_indices:
    val = self.worksheet.cell(row=row, column=self.column_indices['sales tax/ fed in st mode']).value
    invoice_data['sales_tax_fed_st_mode'] = str(val).strip() if val else 'N/A'
```

### 3. **gui.py**

#### Enhanced Data Extraction
```python
sales_tax_fed_st_mode = invoice_data.get('sales_tax_fed_st_mode', 'N/A')
```

#### Enhanced Display Logging
Added to log output:
```python
self.log_message(f"   Sales Tax/FED in ST Mode: {sales_tax_fed_st_mode}")
```

#### Updated Function Call
```python
result = fbr_checker.verify_invoice(
    registration_no, 
    source_authority=source_auth, 
    invoice_no_field=number, 
    date_field=date, 
    sales_tax_fed_st_mode=sales_tax_fed_st_mode
)
```

## How It Works

### Flow Diagram
```
Excel Sheet (with Sales Tax/FED in ST Mode column)
        ↓
gui.py reads data including sales_tax_fed_st_mode
        ↓
excel_handler.py extracts all columns
        ↓
verify_invoice() receives sales_tax_fed_st_mode parameter
        ↓
FBR results table displayed
        ↓
Step 6: Match Logic
    ├─ Use JavaScript to scan table rows
    ├─ Find "Sales Tax/ FED in ST Mode" column header
    ├─ Compare each row's value with Excel value
    ├─ When match found: Click checkbox for that row
    └─ If no match: Click first checkbox (fallback)
        ↓
Continue with Step 7 onwards
```

### Matching Algorithm Details

```javascript
// JavaScript matching logic in Step 6.1
1. Get all table headers
2. Find column index of "Sales Tax/ FED in ST Mode"
3. Iterate through all table rows:
   - Extract the Sales Tax value from the matching column
   - Normalize both values (remove commas, extra spaces)
   - Compare: if values match → found the target row
4. Return the checkbox element of the matching row
5. If no match → return null (fallback to first checkbox)
```

## Excel Column Requirements

The Excel file should contain these columns:
| Column Name | Required | Purpose |
|---|---|---|
| Sr. No | Optional | Serial number |
| Source Authority | Optional | FBR, BRA, KPRA, etc. |
| Seller Name | Optional | Business name |
| Seller Registration No | **Required** | NTN to search |
| Number | Optional | Invoice/Bill number |
| Date | Optional | Invoice date |
| Purchase Type | Optional | Type of goods |
| Rate | Optional | Tax rate % |
| Value of Purchases | Optional | Transaction amount |
| **Sales Tax/ FED in ST Mode** | Optional | **Matching criteria** |

## Usage Example

**Excel Data:**
| Sr.No | Source | Name | Seller Registration No | Number | Date | Sales Tax/ FED in ST Mode |
|---|---|---|---|---|---|---|
| 1536 | SRB | ABDULLAH ENTERPRISES | 4130634888761 | '069 | 30-Sep-2025 | **50,000** |

**FBR Results Table:**
| Checkbox | Invoice # | Seller Name | Amount | Sales Tax/ FED in ST Mode |
|---|---|---|---|---|
| ☐ | 001 | Company A | 100,000 | 30,000 |
| ☐ | 002 | Company B | 200,000 | **50,000** ← Matched! |
| ☐ | 003 | Company C | 150,000 | 25,000 |

**Result:** Only the checkbox for the row with "50,000" will be clicked.

## Backward Compatibility

✅ **Fully backward compatible!**

- If `sales_tax_fed_st_mode` is not provided or is 'N/A', the system falls back to clicking the first checkbox
- Existing code that doesn't pass this parameter will continue to work as before
- Optional parameter ensures no breaking changes

## Logging Output

When processing an invoice with Sales Tax matching:

```
📋 RECORD #1
   Row: 2 | Sr.No: 1536
   Source: SRB | Name: ABDULLAH ENTERPRISES
   Registration No: 4130634888761
   Number: '069 | Date: 30-Sep-2025
   Sales Tax/FED in ST Mode: 50,000
🔍 Verifying on FBR portal...
...
STEP 6.1: Searching for row with Sales Tax/FED in ST Mode = '50,000'...
Found Sales Tax column at index: 4
Row 0 Sales Tax value: 30,000 (looking for: 50,000)
Row 1 Sales Tax value: 50,000 (looking for: 50,000)
MATCH FOUND at row 1
✓ Found matching row for Sales Tax/FED in ST Mode = '50,000'
✓ STEP 6 COMPLETED: Checkbox clicked for matching row (Sales Tax/FED = '50,000')
```

## Error Handling

| Scenario | Behavior |
|---|---|
| Sales Tax column not found in FBR table | Logged as warning, falls back to first checkbox |
| No matching value found | Logged as info, falls back to first checkbox |
| Browser closed | Returns error status |
| Invalid Sales Tax value | Falls back to first checkbox |

## Performance Impact

- **Minimal**: JavaScript matching runs only when `sales_tax_fed_st_mode` is provided
- **String comparisons only**: Fast normalization (remove commas/spaces) before comparison
- **Single pass**: Iterates through rows only once to find match

## Testing Recommendations

1. **Test with matching value**: Verify correct row is selected
2. **Test with non-matching value**: Verify fallback to first checkbox
3. **Test without parameter**: Verify backward compatibility
4. **Test with multiple rows**: Verify only correct row is selected
5. **Test with different number formats**: 
   - "50000"
   - "50,000"
   - "50, 000"
   - Verify all match correctly

## Future Enhancements

Possible improvements:
- [ ] Add fuzzy matching for approximate values (±10%)
- [ ] Support matching on multiple columns simultaneously
- [ ] Add partial matching (startswith, contains)
- [ ] Store matched row details in Excel for audit trail
- [ ] Add option to match on Rate or Value of Purchases instead

## Files Modified

1. `fbr_checker.py` - Enhanced `verify_invoice()` method with matching logic
2. `excel_handler.py` - Added column reading for Sales Tax/FED in ST Mode
3. `gui.py` - Updated to extract and pass new parameter

## Summary

The system now intelligently matches invoice rows from FBR results with Excel data based on the Sales Tax/FED in ST Mode value, ensuring only the correct row is selected for claiming. The implementation is robust, backward-compatible, and includes comprehensive error handling and logging.
