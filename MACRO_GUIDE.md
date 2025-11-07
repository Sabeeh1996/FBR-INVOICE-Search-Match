# 🎬 Macro Recording Feature Guide

## Overview

The FBR Invoice Checker Bot now includes a powerful macro recording and playback feature that allows you to:
- Record your workflow interactions with the FBR portal
- Save and reuse macros for consistent automation
- Edit macro files for fine-tuning
- Share macros with team members

## Key Concepts

### What is a Macro?
A macro is a recorded sequence of browser automation actions (clicks, typing, navigation, etc.) that can be replayed automatically. Macros support template variables like `{invoice_number}` that get replaced with actual values during playback.

### When to Use Macros?
- **Complex workflows**: Multi-step processes beyond simple search
- **Consistency**: Ensure same steps are followed every time
- **Custom verification**: Workflows specific to your organization
- **Troubleshooting**: Test and debug specific action sequences
- **Sharing**: Team members can use the same proven workflow

## Features

### 1. **Normal Mode vs Macro Mode**
- **Normal Mode**: Uses built-in FBR verification logic
- **Macro Mode**: Plays back a recorded macro for each invoice

### 2. **Recording Actions**
The recorder captures:
- Navigation to URLs
- Clicking buttons/links
- Entering text (with template support)
- Waiting for elements
- Taking screenshots
- Assertions to validate results

### 3. **Template Variables**
Use placeholders in your macros:
- `{invoice_number}` - Current invoice being processed
- `{row_number}` - Excel row number

### 4. **Error Handling**
- Automatic retries with exponential backoff
- Screenshot capture on failures
- Continue or halt on errors (configurable)
- Detailed error logs

## How to Use

### Recording a New Macro

1. **Start Recording**
   - Click **⏺ Record** button
   - Enter a name for your macro (e.g., "fbr_invoice_check")
   - Click OK

2. **Perform Workflow Manually**
   - The bot will open Chrome browser
   - Manually perform the invoice check steps
   - All your actions on key elements will be recorded

3. **Stop Recording**
   - Click **⏹ Stop** button
   - Choose to save or discard
   - Macro is saved to `macros/` folder as JSON

### Using an Existing Macro

1. **Select Macro Mode**
   - Choose "Macro Mode" radio button

2. **Select Macro**
   - Pick a macro from the dropdown
   - Click **⟳ Refresh** to reload list

3. **Start Processing**
   - Select your Excel file
   - Click **▶ Start**
   - Watch the macro replay for each invoice

### Managing Macros

#### **📂 Load Macro**
- Import macro from any location
- Useful for sharing macros between computers

#### **✏️ Edit Macro**
- Opens JSON editor
- Modify actions, selectors, timeouts
- Validates JSON before saving

#### **🗑️ Delete Macro**
- Remove unwanted macros from library
- Confirmation required

## Macro File Structure

Macros are stored as JSON files in the `macros/` folder:

```json
{
  "version": 1,
  "name": "FBR Invoice Check Sample",
  "created_at": "2025-11-07T00:00:00",
  "duration": 45.5,
  "action_count": 8,
  "metadata": {
    "description": "Sample macro for checking FBR invoice status",
    "author": "FBR Invoice Checker Bot",
    "variables": ["invoice_number", "row_number"]
  },
  "actions": [
    {
      "action": "navigate",
      "selector": "",
      "selector_type": "xpath",
      "value": "https://iris.fbr.gov.pk/",
      "timeout": 10.0,
      "retries": 3,
      "description": "Navigate to FBR portal",
      "meta": {"critical": true}
    },
    {
      "action": "send_keys",
      "selector": "//input[@id='invoiceNumber']",
      "selector_type": "xpath",
      "value": "{invoice_number}",
      "timeout": 10.0,
      "retries": 3,
      "description": "Enter invoice number",
      "meta": {"critical": true}
    },
    {
      "action": "click",
      "selector": "//button[@id='searchBtn']",
      "selector_type": "xpath",
      "value": "",
      "timeout": 10.0,
      "retries": 3,
      "description": "Click search button",
      "meta": {"critical": true}
    }
  ]
}
```

## Action Types

| Action | Description | Example |
|--------|-------------|---------|
| `navigate` | Go to URL | `"value": "https://fbr.gov.pk"` |
| `click` | Click element | `"selector": "//button[@id='submit']"` |
| `send_keys` | Type text (clears field first) | `"value": "{invoice_number}"` |
| `send_keys_append` | Type text (appends) | `"value": "additional text"` |
| `wait` | Fixed delay | `"value": "2"` (seconds) |
| `wait_for_element` | Wait for element | `"meta": {"condition": "visible"}` |
| `assert_text` | Verify text present | `"value": "Claimed"` |
| `assert_element` | Verify element exists | `"selector": "//div[@id='result']"` |
| `screenshot` | Capture screenshot | `"value": "invoice_{invoice_number}"` |
| `get_text` | Read element text | Logs to console |

## Selector Types

- **xpath**: XPath expressions (most flexible)
  - Example: `//input[@id='invoiceNo']`
  - Example: `//button[contains(text(),'Search')]`
  
- **css**: CSS selectors (faster)
  - Example: `#invoiceNo`
  - Example: `.search-button`
  
- **id**: Element ID (most reliable when available)
  - Example: `invoices_tabview:STform:invoiceNo`

## Action Properties

### Required
- `action`: Action type (see Action Types above)
- `selector`: Element selector (empty for some actions like navigate/wait)
- `selector_type`: "xpath", "css", or "id"

### Optional
- `value`: Value for action (URL, text to type, etc.)
- `timeout`: Seconds to wait for element (default: 10.0)
- `retries`: Number of retry attempts (default: 3)
- `description`: Human-readable description
- `meta`: Additional metadata
  - `critical`: If true, stop playback on failure
  - `condition`: For wait_for_element - "visible" or "clickable"

## Best Practices

### 1. **Use Robust Selectors**
   - Prefer IDs over classes
   - Use stable attributes
   - Avoid brittle XPaths with indices

   ❌ Bad: `//div[1]/div[2]/input[3]`
   ✅ Good: `//input[@id='invoiceNumber']`

### 2. **Add Wait Actions**
   - Wait after clicks/submissions
   - Use `wait_for_element` for dynamic content
   
   ```json
   {
     "action": "click",
     "selector": "//button[@id='search']"
   },
   {
     "action": "wait",
     "value": "2"
   }
   ```

### 3. **Mark Critical Actions**
   - Set `"critical": true` for must-succeed steps
   - Non-critical failures won't stop playback
   
   ```json
   {
     "action": "click",
     "selector": "//button[@id='submit']",
     "meta": {"critical": true}
   }
   ```

### 4. **Use Template Variables**
   - Always use `{invoice_number}` not hardcoded values
   - Macros won't work for batch processing otherwise
   
   ❌ Bad: `"value": "12345678"`
   ✅ Good: `"value": "{invoice_number}"`

### 5. **Add Screenshots**
   - Capture results for audit trail
   - Screenshots saved to `logs/screenshots/`
   
   ```json
   {
     "action": "screenshot",
     "value": "result_{invoice_number}"
   }
   ```

### 6. **Test Before Batch Run**
   - Test macro with 1-2 invoices first
   - Check logs for any warnings
   - Verify Excel results are correct

## Troubleshooting

### Problem: Macro fails to find elements
**Solution**: 
- Check if selectors are correct
- Increase timeout value
- Add `wait_for_element` before action
- Verify FBR website hasn't changed

### Problem: Macro works for one invoice but fails on others
**Solution**:
- Ensure you're using `{invoice_number}` template
- Check if state carries over between runs
- Add navigation to reset state

### Problem: Recording doesn't capture all actions
**Solution**:
- Not all actions can be auto-recorded
- Manually edit JSON to add missing steps
- Focus on key elements (input fields, buttons)

### Problem: Playback is too fast
**Solution**:
- Increase timeouts
- Add more `wait` actions
- Check `step_delay` in player (default: 0.5s)

## Advanced Usage

### Dry Run Mode
Test macro without making changes:
```python
result = macro_player.play(actions, context=context, dry_run=True)
```

### Custom Context Variables
Add your own variables:
```python
context = {
    "invoice_number": "12345678",
    "row_number": "10",
    "custom_field": "value"
}
```

### Conditional Logic
Use assertions for branching:
```json
{
  "action": "assert_text",
  "selector": "//div[@id='status']",
  "value": "Success",
  "meta": {"critical": false}
}
```

## Security Considerations

⚠️ **Important Security Notes:**

1. **Never store passwords in macros**
   - Macros are plain text JSON
   - Use manual login before running macros
   - Credentials should be handled separately

2. **Review macros before sharing**
   - May contain sensitive URLs
   - May contain business logic

3. **Validate macro source**
   - Only load macros from trusted sources
   - Review JSON before running

## Example Workflows

### Basic Invoice Check
1. Navigate to FBR portal
2. Wait for page load
3. Enter invoice number
4. Click search
5. Wait for results
6. Screenshot result

### Advanced Verification
1. Navigate to FBR portal
2. Handle login (if needed)
3. Navigate to invoice section
4. Enter invoice number
5. Click search
6. Wait for results table
7. Assert "Claimed" text present
8. Screenshot result
9. Extract additional data

## Tips & Tricks

- **Macro Library**: Organize macros by function (e.g., `fbr_basic_check.json`, `fbr_detailed_check.json`)
- **Version Control**: Keep macros in Git for team collaboration
- **Testing**: Create test macros with known invoice numbers
- **Documentation**: Add detailed descriptions in macro metadata
- **Backup**: Copy working macros before editing

## Support

For issues or questions:
1. Check logs in `logs/` folder
2. Review this guide
3. Examine sample macro: `macros/sample_fbr_check.json`
4. Edit and test macros incrementally

---

**Happy Automating! 🎉**
