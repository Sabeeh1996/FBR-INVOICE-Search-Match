# EXPIRY SYSTEM - VISUAL GUIDE & DIAGRAMS

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    FBR Invoice Checker Bot                   │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Application Startup (main.py)            │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │         Initialize License Manager                    │   │
│  │   ┌────────────────────────────────────────────┐    │   │
│  │   │ Load license_config.json                   │    │   │
│  │   │ OR create with DEFAULT_EXPIRY_DATE         │    │   │
│  │   └────────────────────────────────────────────┘    │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↓                                   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │     Validate License (is_expired check)              │   │
│  └──────────────────────────────────────────────────────┘   │
│                           ↓                                   │
│         ╔═════════════════╦═════════════════╗              │
│         ║ Expired?        ║ Not Expired?     ║              │
│         ║ (days < 0)      ║ (days >= 0)      ║              │
│         ╚════════╤════════╩════════╤═════════╝              │
│                  ↓                  ↓                        │
│          ┌──────────────┐   ┌──────────────────┐           │
│          │ SHOW ERROR   │   │ Show GUI          │           │
│          │ & EXIT ❌    │   │ Display Status    │           │
│          └──────────────┘   └──────────────────┘           │
│                                      ↓                       │
│                          ┌───────────────────────┐          │
│                          │ Display License Bar   │          │
│                          │ (Color-coded Status)  │          │
│                          └───────────────────────┘          │
│                                      ↓                       │
│                       ╔═════════════════════╗              │
│                       ║ Status Level Check   ║              │
│                       ╚════════╤════════════╝              │
│            ┌──────────┬────────┼────────┬──────────┐       │
│            ↓          ↓        ↓        ↓          ↓       │
│        ┌────────┐ ┌─────┐ ┌────────┐ ┌──────┐ ┌──────┐  │
│        │ OK     │ │WARN │ │CRITICAL│ │EXPIRE│ │RUN   │  │
│        │(>30d)  │ │(7-30)│ │(<7d)  │ │(<=0) │ │NORMAL│  │
│        └────────┘ └─────┘ └────────┘ └──────┘ └──────┘  │
│        No Dialog  Info DLG Warning   Error DLG           │
│                                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## Status Timeline

```
       Today              7 Days          30 Days        After
        ▼                  ▼               ▼             Expiry
        |                  |               |               |
        |                  |               |               |
────┼──────────────────┼──────────────────┼───────────────┼────────
    |                  |                  |               |
    |                  |                  |               |
    ↓                  ↓                  ↓               ↓
   EXPIRED           CRITICAL            WARNING          OK
  🔴 Red              🔴 Red             🟡 Orange       🟢 Green
  BLOCKED        Show Critical Warn  Show Info Warn   Continue
  Cannot Run     7 days left         30 days left     No Issues

Status: EXPIRED        Status: CRITICAL      Status: WARNING      Status: OK
Days:   -10 days       Days:   5 days        Days:   20 days      Days:   100 days
Action: BLOCK          Action: WARN          Action: NOTIFY       Action: CONTINUE
User:   CAN'T START    User:   URGENT        User:   INFO         User:   NORMAL
```

---

## Status Display Colors

```
┌─────────────────────────────────────────────────────────────┐
│ FBR Invoice Checker Bot - Status Bar                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  OK Status (> 30 days remaining):                            │
│  ┌──────────────────────────────────────────────────────┐   │
│  │🟢 ✓ Software active. Expires in 365 days (2026-12-31)   │   │
│  │                                                  [Details]│   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  WARNING Status (7-30 days remaining):                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │🟡 WARNING: Software expires in 15 days (2024-11-28)      │   │
│  │                                                  [Details]│   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  CRITICAL Status (0-6 days remaining):                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │🔴 CRITICAL: Software expires in 5 days (2024-11-18)      │   │
│  │                                                  [Details]│   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
│  EXPIRED Status (Past expiry date):                          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │🔴 SOFTWARE EXPIRED! Expired on 2024-11-10              │   │
│  │                                                  [Details]│   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagram

```
                    ┌─────────────────┐
                    │  Admin Tool     │
                    │ (set_expiry.py) │
                    └────────┬────────┘
                             │
                    Sets/Updates Expiry
                             │
                             ↓
                    ┌─────────────────────┐
                    │ license_config.json │
                    │                     │
                    │ {                   │
                    │   expiry_date: ...  │
                    │   created_date: ... │
                    │   last_updated: ... │
                    │ }                   │
                    └────────┬────────────┘
                             │
              ┌──────────────┼──────────────┐
              ↓              ↓              ↓
        ┌──────────┐  ┌──────────┐  ┌──────────┐
        │ main.py  │  │  gui.py  │  │ Status   │
        │          │  │          │  │ Checks   │
        │Load      │  │ Display  │  │          │
        │Validate  │  │ Status   │  │ Expired? │
        └────┬─────┘  └────┬─────┘  │ Days Left│
             │             │        │ Level    │
             │             │        └────┬─────┘
             │             │             │
      Logs info      Shows at top   Determines
      & continues    of window      Color & Dialog
```

---

## Admin Workflow

```
START
  ↓
┌─────────────────────────────────┐
│ Admin needs to set expiry date  │
└────────┬────────────────────────┘
         │
         ├────────────────────────────────────────────┐
         │                                            │
         ↓                                            ↓
┌──────────────────────────┐        ┌───────────────────────┐
│ Option 1: GUI Tool       │        │ Option 2: Command Line│
├──────────────────────────┤        ├───────────────────────┤
│                          │        │                       │
│ python set_expiry.py gui │        │ python set_expiry.py  │
│                          │        │ 2025-12-31            │
│ ┌────────────────────┐   │        │                       │
│ │ Window opens       │   │        │ ┌─────────────────┐   │
│ │ Shows current date │   │        │ │ Command executes│   │
│ │ Prompts for input  │   │        │ │ in terminal     │   │
│ │ Enter: 2025-12-31  │   │        │ │                 │   │
│ │ Click OK           │   │        │ │ Shows: Success  │   │
│ │                    │   │        │ │ ✓ Updated!      │   │
│ └────────────────────┘   │        │ └─────────────────┘   │
└──────────┬───────────────┘        └──────────┬────────────┘
           │                                   │
           └───────────────────┬───────────────┘
                               │
                        BOTH OPTIONS
                        Update config
                               │
                               ↓
                    ┌────────────────────┐
                    │ license_config.json│
                    │ Updated! ✓         │
                    └────────┬───────────┘
                             │
                             ↓
                    ┌────────────────────┐
                    │ Restart Application│
                    │ python main.py     │
                    └────────┬───────────┘
                             │
                             ↓
                    ┌────────────────────┐
                    │ New expiry date    │
                    │ in effect! ✓       │
                    └────────────────────┘
                             │
                           END
```

---

## User Experience Timeline

```
Month 1 ────────────────────────────────────────────
  ↓
User installs software
Status: ✓ OK (Green)
Experience: Normal, no warnings
Event Log: License loaded, 365 days remaining

Month 10 ───────────────────────────────────────────
  ↓
User runs software
Status: 🟡 WARNING (Orange)
Experience: Warning dialog appears
Message: "Software expires in 30 days"
Event Log: Warning level triggered

Month 11 ───────────────────────────────────────────
  ↓
User runs software
Status: 🔴 CRITICAL (Red)
Experience: Critical warning dialog appears
Message: "Software expires in 7 days!"
Action: Admin should renew license NOW
Event Log: Critical level triggered

Month 11 (Day 5) ───────────────────────────────────
  ↓
Admin runs: python set_expiry.py 2025-12-31
Response: ✓ Updated successfully!
Status: Updated to new date

Month 11 (Day 6) ───────────────────────────────────
  ↓
User restarts software
Status: ✓ OK (Green) - Back to normal!
Experience: No more warnings
Event Log: License renewed, 365 days remaining

Month 12 ────────────────────────────────────────────
  ↓
...Cycle repeats...
```

---

## Error Handling Flow

```
┌─────────────────────────────────┐
│ Try to load license_config.json │
└────────────┬────────────────────┘
             │
       ┌─────┴─────┐
       │           │
    Exists?    Missing?
       │           │
       ↓           ↓
    ┌────┐    ┌──────────────────┐
    │Load│    │Create with       │
    │File│    │DEFAULT_EXPIRY    │
    └─┬──┘    │Save to disk      │
      │       └────────┬─────────┘
      │                │
      └────────┬───────┘
               │
               ↓
    ┌─────────────────┐
    │Parse JSON       │
    └────┬────────────┘
         │
    ┌────┴────────────────┐
    │                     │
Valid JSON?          Invalid JSON?
    │                     │
    ↓                     ↓
  Parse          Log Error & Use
  Success        Default Date
    │                     │
    └────────┬────────────┘
             │
             ↓
    ┌─────────────────┐
    │Validate Date    │
    │Format YYYY-MM-DD│
    └────┬────────────┘
         │
    ┌────┴──────────────────┐
    │                       │
  Valid Format?      Invalid Format?
    │                       │
    ↓                       ↓
  Continue            Error Message
                      Use Fallback
```

---

## File Relationships

```
┌─────────────────────────────────────────────────────────┐
│                    license_manager.py                    │
│                                                           │
│  ┌────────────────────────────────────────────────────┐ │
│  │ class LicenseManager                               │ │
│  │ - load_or_create_config()                          │ │
│  │ - save_config()                                    │ │
│  │ - set_expiry_date(date_str)                        │ │
│  │ - get_days_until_expiry()                          │ │
│  │ - is_expired()                                     │ │
│  │ - get_expiry_status()                              │ │
│  │ - validate_license()                               │ │
│  │ - show_expiry_warning()                            │ │
│  └────────────────────────────────────────────────────┘ │
└──────────────┬──────────────────────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
    ↓          ↓          ↓
┌────────┐ ┌──────────┐ ┌────────┐
│main.py │ │  gui.py  │ │set_exp │
│        │ │          │ │iry.py  │
│ Uses   │ │ Uses     │ │ Uses   │
│License │ │License   │ │License │
│Manager │ │Manager   │ │Manager │
└────────┘ └──────────┘ └────────┘
     │          │          │
     └──────────┼──────────┘
                │
                ↓
      ┌─────────────────────┐
      │ license_config.json │
      │ (License data)      │
      └─────────────────────┘
```

---

## Decision Tree - What Should User See?

```
                       Application Starts
                             ↓
                      ┌──────────────┐
                      │ Load License │
                      └──────┬───────┘
                             ↓
                        ┌─────────────┐
                        │ Get Status  │
                        └──────┬──────┘
                               ↓
            ┌──────────────────┼──────────────────┐
            ↓                  ↓                  ↓
        Days < 0           Days 0-6          Days 7-30
       ┌─────────┐        ┌──────────┐       ┌─────────┐
       │ EXPIRED │        │ CRITICAL │       │ WARNING │
       └────┬────┘        └────┬─────┘       └────┬────┘
            │                  │                   │
            ↓                  ↓                   ↓
        ┌─────────────────────────────────────────────────┐
        │               Show Status Bar                    │
        │            (Color: Red / Red / Orange)           │
        └──────────────┬──────────────────────────────────┘
                       │
            ┌──────────┴──────────┐
            │                     │
            ↓                     ↓
       ┌─────────────┐     ┌─────────────┐
       │ Show Error  │     │ Show Dialog │
       │ Dialog:     │     │ Level:      │
       │ "Expired"   │     │ Warn/Critical
       │ Exit ❌     │     │ Continue ✓  │
       └─────────────┘     └─────────────┘
```

---

## Quick Reference Icons

| Icon | Meaning |
|------|---------|
| 🟢 | Green - Everything OK |
| 🟡 | Orange - Warning |
| 🔴 | Red - Critical or Expired |
| ✓ | Success / OK |
| ❌ | Error / Failed |
| ⚠️ | Warning |
| 📋 | Information |
| 🔒 | Locked / Expired |

---

## Testing Flow Diagram

```
START TEST
    ↓
┌────────────────────────────────┐
│ Set Expiry in Future (>30 days)│
└─────────┬──────────────────────┘
          ↓
┌────────────────────────────────┐
│ Run Application                │
│ Expected: Green Status, No Warn│
└─────────┬──────────────────────┘
          ↓
┌────────────────────────────────┐
│ Set Expiry Soon (7-30 days)    │
└─────────┬──────────────────────┘
          ↓
┌────────────────────────────────┐
│ Run Application                │
│ Expected: Orange, Info Dialog  │
└─────────┬──────────────────────┘
          ↓
┌────────────────────────────────┐
│ Set Expiry Critical (<7 days)  │
└─────────┬──────────────────────┘
          ↓
┌────────────────────────────────┐
│ Run Application                │
│ Expected: Red, Warning Dialog  │
└─────────┬──────────────────────┘
          ↓
┌────────────────────────────────┐
│ Set Expiry Past (already expired)│
└─────────┬──────────────────────┘
          ↓
┌────────────────────────────────┐
│ Try to Run Application         │
│ Expected: Error Dialog, Exit ❌│
└─────────┬──────────────────────┘
          ↓
END TEST ✓
```

---

This visual guide helps understand the expiry system architecture and flow.
