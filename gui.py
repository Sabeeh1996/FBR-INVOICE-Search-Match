"""
GUI Module
Interactive Tkinter-based GUI for FBR Invoice Checker Bot.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import threading
import logging
from excel_handler import ExcelHandler
from fbr_checker import FBRChecker
import time
import random
import json
import asyncio
from pathlib import Path
import os

try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    logging.warning("PIL not installed. Logo will not be displayed. Install with: pip install Pillow")

# -----------------------------
# Theme 1 - Modern Light Colors
# -----------------------------
WINDOW_BG = "#F5F6FA"          # main app background
PANEL_BG = "#FFFFFF"           # panels, frames, group boxes
TITLE_TEXT = "#2C3E50"         # main headings
NORMAL_TEXT = "#2C3E50"        # labels, small headings
SUB_TEXT = "#7F8C8D"           # status text or helper labels
BORDER_COLOR = "#D5D8DC"       # frame borders, separators
INPUT_BG = "#FFFFFF"           # entry, textbox background
INPUT_BORDER = "#D0D3D4"       # entry borders
SCROLLBAR_COLOR = "#BDC3C7"

# Buttons
BTN_START_BG = "#27AE60"
BTN_START_HOVER = "#1E8449"
BTN_EXIT_BG = "#E74C3C"
BTN_EXIT_HOVER = "#C0392B"
BTN_BROWSE_BG = "#3498DB"
BTN_BROWSE_HOVER = "#216FAD"
BTN_TEXT = "#FFFFFF"

# Progress display colors
CLAIMED_COLOR = "#27AE60"
NOT_CLAIMED_COLOR = "#E74C3C"
ERROR_COLOR = "#F39C12"
PROGRESS_TRACK = "#E5E7E9"
PROGRESS_FILL = "#3498DB"

# Default fonts
DEFAULT_FONT = ("Arial", 10)
TITLE_FONT = ("Arial", 18, "bold")
# -----------------------------

try:
    from playwright.async_api import async_playwright, Page
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not installed. Recording feature disabled. Install with: pip install playwright")


class FBRInvoiceCheckerGUI:
    """
    Main GUI application for FBR Invoice Checker Bot.
    Provides an interactive interface for invoice verification.
    """
    
    def __init__(self, root, license_manager=None):
        """
        Initialize the GUI application.
        
        Args:
            root: Tkinter root window
            license_manager: License manager instance for expiry checks
        """
        self.root = root
        self.root.title("🧾 FBR Invoice Checker Bot v2.1")
        # Start with a reasonable default size but allow resizing for responsiveness
        self.root.geometry("900x650")
        self.root.minsize(720, 480)
        self.root.resizable(True, True)
        
        # License manager
        self.license_manager = license_manager
        
        # Variables
        self.excel_file_path = tk.StringVar()
        self.is_running = False
        self.is_paused = False
        self.worker_thread = None
        
        # Pause/Resume tracking
        self.pause_requested = False
        self.last_processed_row = None
        self.current_mode = None  # 'verify' or 'stwh'
        
        # Workflow indicator state
        self.workflow_indicator = None
        
        # Persistent instances
        self.fbr_checker = None
        self.excel_handler = None
        
        # Recording variables
        self.is_recording = False
        self.recorded_steps = []
        self.browser = None
        self.page = None
        self.playwright_instance = None
        self.recording_loop = None
        # Recorder UI widget placeholders (removed from UI but kept to avoid attribute errors)
        self.record_btn = None
        self.stop_record_btn = None
        self.extract_text_btn = None
        self.save_recording_btn = None
        self.clear_recording_btn = None
        
        # Statistics
        self.total_invoices = 0
        self.processed_count = 0
        self.claimed_count = 0
        self.not_claimed_count = 0
        self.error_count = 0
        
        # Timing variables
        self.start_time = None
        self.end_time = None
        
        # Setup GUI
        self.setup_gui()
        
        # Show welcome message and expiry warning if needed
        self.show_welcome_message()
        
        # Show expiry warning if software is expiring soon
        if self.license_manager:
            status = self.license_manager.get_expiry_status()
            if status['should_show_warning']:
                self.license_manager.show_expiry_warning(self.root)
    
    def setup_gui(self):
        """
        Setup all GUI components with responsive layout.
        """
        # Apply global background and configure root for theming
        self.root.configure(bg=WINDOW_BG)
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Setup ttk style for theme
        style = ttk.Style()
        # Use default theme as base then override
        try:
            style.theme_use('clam')
        except Exception:
            pass

        # Frame and panel styles
        style.configure('Main.TFrame', background=WINDOW_BG)
        style.configure('Panel.TLabelframe', background=PANEL_BG, bordercolor=BORDER_COLOR)
        style.configure('Panel.TLabelframe.Label', background=PANEL_BG, foreground=TITLE_TEXT, font=DEFAULT_FONT)
        style.configure('Panel.TFrame', background=PANEL_BG)

        # Label styles
        style.configure('Title.TLabel', background=WINDOW_BG, foreground=TITLE_TEXT, font=TITLE_FONT)
        style.configure('Normal.TLabel', background=PANEL_BG, foreground=NORMAL_TEXT, font=DEFAULT_FONT)
        style.configure('Sub.TLabel', background=PANEL_BG, foreground=SUB_TEXT, font=("Arial", 9))

        # Entry style
        style.configure('Custom.TEntry', fieldbackground=INPUT_BG, background=INPUT_BG, foreground=NORMAL_TEXT, bordercolor=INPUT_BORDER, padding=6)

        # Progressbar style
        style.configure('Custom.Horizontal.TProgressbar', troughcolor=PROGRESS_TRACK, background=PROGRESS_FILL, thickness=14)

        # Button styles (normal and hover variants)
        style.configure('Start.TButton', foreground=BTN_TEXT, background=BTN_START_BG, padding=8, relief='flat')
        style.map('Start.TButton', 
                  background=[('active', BTN_START_HOVER), ('disabled', '#A0A0A0')],
                  foreground=[('disabled', '#FFFFFF')])
        style.configure('StartHover.TButton', foreground=BTN_TEXT, background=BTN_START_HOVER)

        style.configure('Exit.TButton', foreground=BTN_TEXT, background=BTN_EXIT_BG, padding=8, relief='flat')
        style.map('Exit.TButton', 
                  background=[('active', BTN_EXIT_HOVER), ('disabled', '#A0A0A0')],
                  foreground=[('disabled', '#FFFFFF')])
        style.configure('ExitHover.TButton', foreground=BTN_TEXT, background=BTN_EXIT_HOVER)

        style.configure('Browse.TButton', foreground=BTN_TEXT, background=BTN_BROWSE_BG, padding=6, relief='flat')
        style.map('Browse.TButton', 
                  background=[('active', BTN_BROWSE_HOVER), ('disabled', '#A0A0A0')],
                  foreground=[('disabled', '#FFFFFF')])
        style.configure('BrowseHover.TButton', foreground=BTN_TEXT, background=BTN_BROWSE_HOVER)

        # Scrollbar style
        style.configure('Vertical.TScrollbar', background=SCROLLBAR_COLOR, troughcolor=SCROLLBAR_COLOR)

        # Main container with padding - responsive
        main_frame = ttk.Frame(self.root, padding="15", style='Main.TFrame')
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure main frame columns and rows for responsiveness
        main_frame.columnconfigure(0, weight=1)
        # Row weights will be set after we know if license frame is created
        
        # Title with version
        title_label = ttk.Label(
            main_frame, 
            text="🧾 FBR Invoice Checker Bot v2.1", 
            style='Title.TLabel',
            wraplength=600
        )
        title_label.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # License status bar (only show for non-OK status)
        license_frame_created = False
        if self.license_manager:
            status = self.license_manager.get_expiry_status()
            
            # Only show the license bar if status is not OK
            if status['status_level'] != 'OK':
                status_color = {
                    'WARNING': '#FFAA00',      # Orange
                    'CRITICAL': '#FF5500',     # Red-Orange
                    'EXPIRED': '#FF0000'       # Red
                }
                bg_color = status_color.get(status['status_level'], '#CCCCCC')
                
                license_frame = ttk.Frame(main_frame, style='Panel.TFrame')
                license_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
                license_frame_created = True
                
                # Create a label with background color (using a workaround)
                license_label = tk.Label(
                    license_frame,
                    text=f"📋 {status['message']}",
                    bg=bg_color,
                    fg=BTN_TEXT,
                    font=("Arial", 9),
                    pady=5,
                    padx=10,
                    wraplength=500
                )
                license_label.pack(fill=tk.X, side=tk.LEFT, expand=True)
                
                # Add a help button to show more details
                def show_license_details():
                    messagebox.showinfo(
                        "License Information",
                        self.license_manager.get_expiry_info_text()
                    )
                
                help_btn = ttk.Button(
                    license_frame,
                    text="Details",
                    command=show_license_details,
                    width=10
                )
                help_btn.pack(side=tk.RIGHT, padx=5)
        
        # Set expandable row for logs (row index depends on whether license frame is shown)
        # Logs will be at row 6 if license shown, row 5 if not (since we added elapsed time row)
        main_frame.rowconfigure((6 if license_frame_created else 5), weight=1)
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="Excel File Selection", padding="10", style='Panel.TLabelframe')
        file_frame.grid(row=(2 if license_frame_created else 1), column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)
        
        ttk.Label(file_frame, text="Excel File:", style='Normal.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        file_entry = ttk.Entry(file_frame, textvariable=self.excel_file_path, state='readonly', style='Custom.TEntry')
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="Browse...", command=self.browse_file, style='Browse.TButton')
        browse_btn.grid(row=0, column=2, padx=(5, 0))

        # Hover effects for browse
        def _on_enter(btn, hover_style):
            try:
                btn.configure(style=hover_style)
            except Exception:
                pass

        def _on_leave(btn, normal_style):
            try:
                btn.configure(style=normal_style)
            except Exception:
                pass

        browse_btn.bind('<Enter>', lambda e: _on_enter(browse_btn, 'BrowseHover.TButton'))
        browse_btn.bind('<Leave>', lambda e: _on_leave(browse_btn, 'Browse.TButton'))
        
        # Control buttons - centered with proper spacing
        button_frame = ttk.Frame(main_frame, style='Main.TFrame')
        button_frame.grid(row=(3 if license_frame_created else 2), column=0, pady=(0, 15))
        
        # Create inner frame for centered buttons
        inner_button_frame = ttk.Frame(button_frame)
        inner_button_frame.pack(expand=True)
        
        self.start_btn = ttk.Button(
            inner_button_frame, 
            text="🌐 Open FBR Portal", 
            command=self.start_fbr_browser,
            width=18,
            style='Start.TButton'
        )
        self.start_btn.grid(row=0, column=0, padx=8, pady=5)
        
        self.verify_btn = ttk.Button(
            inner_button_frame, 
            text="▶ Verify Invoices", 
            command=self.start_verification,
            width=18,
            state='disabled',
            style='Start.TButton'
        )
        self.verify_btn.grid(row=0, column=1, padx=8, pady=5)
        
        self.load_stwh_btn = ttk.Button(
            inner_button_frame, 
            text="📥 LOAD STWH", 
            command=self.start_load_stwh,
            width=18,
            state='disabled',
            style='Start.TButton'
        )
        self.load_stwh_btn.grid(row=0, column=2, padx=8, pady=5)
        
        self.pause_btn = ttk.Button(
            inner_button_frame, 
            text="⏸ Pause", 
            command=self.pause_processing,
            width=12,
            state='disabled',
            style='Start.TButton'
        )
        self.pause_btn.grid(row=0, column=3, padx=4, pady=5)
        self.pause_btn.grid_remove()  # Hide initially
        
        self.resume_btn = ttk.Button(
            inner_button_frame, 
            text="▶ Resume", 
            command=self.resume_processing,
            width=12,
            state='normal',
            style='Start.TButton'
        )
        self.resume_btn.grid(row=0, column=4, padx=4, pady=5)
        self.resume_btn.grid_remove()  # Hide initially
        
        self.stop_btn = ttk.Button(
            inner_button_frame, 
            text="⏹ Stop", 
            command=self.stop_processing,
            width=12,
            state='disabled',
            style='Exit.TButton'
        )
        self.stop_btn.grid(row=0, column=5, padx=4, pady=5)
        self.stop_btn.grid_remove()  # Hide initially
        
        # Separator space before Exit button
        ttk.Frame(inner_button_frame, width=30).grid(row=0, column=6)
        
        self.exit_btn = ttk.Button(
            inner_button_frame, 
            text="✖ Exit", 
            command=self.exit_application,
            width=12,
            style='Exit.TButton'
        )
        self.exit_btn.grid(row=0, column=7, padx=8, pady=5)

        # Hover effects for start and exit
        self.start_btn.bind('<Enter>', lambda e: _on_enter(self.start_btn, 'StartHover.TButton'))
        self.start_btn.bind('<Leave>', lambda e: _on_leave(self.start_btn, 'Start.TButton'))
        self.exit_btn.bind('<Enter>', lambda e: _on_enter(self.exit_btn, 'ExitHover.TButton'))
        self.exit_btn.bind('<Leave>', lambda e: _on_leave(self.exit_btn, 'Exit.TButton'))
        
        # Recording controls have been removed from the UI
        
        # Progress section - fully responsive
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10", style='Panel.TLabelframe')
        progress_frame.grid(row=(4 if license_frame_created else 3), column=0, sticky=(tk.W, tk.E), pady=(0, 15))
        progress_frame.columnconfigure(0, weight=1)
        
        # Let progress bar expand horizontally with the window
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate',
            style='Custom.Horizontal.TProgressbar'
        )
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Progress label - responsive
        self.progress_label = ttk.Label(progress_frame, text="Ready to start", style='Normal.TLabel', wraplength=600)
        self.progress_label.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Workflow indicator frame
        workflow_frame = ttk.Frame(progress_frame, style='Panel.TFrame')
        workflow_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        tk.Label(workflow_frame, text="🔄 Active Workflow:", font=("Arial", 10, "bold"), bg=PANEL_BG, fg=SUB_TEXT).pack(side=tk.LEFT, padx=5)
        self.workflow_indicator = tk.Label(workflow_frame, text="None", font=("Arial", 10, "bold"), bg=PANEL_BG, fg=NORMAL_TEXT)
        self.workflow_indicator.pack(side=tk.LEFT, padx=5)
        
        # Statistics frame - responsive with wrapping
        stats_frame = ttk.Frame(progress_frame, style='Panel.TFrame')
        stats_frame.grid(row=3, column=0, sticky=(tk.W, tk.E))
        stats_frame.columnconfigure(1, weight=1)
        stats_frame.columnconfigure(3, weight=1)
        stats_frame.columnconfigure(5, weight=1)
        stats_frame.columnconfigure(7, weight=1)
        
        tk.Label(stats_frame, text="Total:", font=("Arial", 9, "bold"), bg=PANEL_BG, fg=NORMAL_TEXT).grid(row=0, column=0, padx=5, sticky=tk.W)
        self.total_label = tk.Label(stats_frame, text="0", font=("Arial", 9), bg=PANEL_BG, fg=NORMAL_TEXT)
        self.total_label.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        tk.Label(stats_frame, text="✅ Claimed:", font=("Arial", 9, "bold"), bg=PANEL_BG, fg=CLAIMED_COLOR).grid(row=0, column=2, padx=5, sticky=tk.W)
        self.claimed_label = tk.Label(stats_frame, text="0", font=("Arial", 9), bg=PANEL_BG, fg=CLAIMED_COLOR)
        self.claimed_label.grid(row=0, column=3, padx=5, sticky=tk.W)
        
        tk.Label(stats_frame, text="❌ Not Claimed:", font=("Arial", 9, "bold"), bg=PANEL_BG, fg=NOT_CLAIMED_COLOR).grid(row=0, column=4, padx=5, sticky=tk.W)
        self.not_claimed_label = tk.Label(stats_frame, text="0", font=("Arial", 9), bg=PANEL_BG, fg=NOT_CLAIMED_COLOR)
        self.not_claimed_label.grid(row=0, column=5, padx=5, sticky=tk.W)
        
        tk.Label(stats_frame, text="⚠️ Errors:", font=("Arial", 9, "bold"), bg=PANEL_BG, fg=ERROR_COLOR).grid(row=0, column=6, padx=5, sticky=tk.W)
        self.error_label = tk.Label(stats_frame, text="0", font=("Arial", 9), bg=PANEL_BG, fg=ERROR_COLOR)
        self.error_label.grid(row=0, column=7, padx=5, sticky=tk.W)
        
        # Timing frame - show start and end times
        timing_frame = ttk.Frame(progress_frame, style='Panel.TFrame')
        timing_frame.grid(row=4, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        timing_frame.columnconfigure(1, weight=1)
        timing_frame.columnconfigure(3, weight=1)
        
        tk.Label(timing_frame, text="⏱️ Start Time:", font=("Arial", 9, "bold"), bg=PANEL_BG, fg=SUB_TEXT).grid(row=0, column=0, padx=5, sticky=tk.W)
        self.start_time_label = tk.Label(timing_frame, text="--:-- --", font=("Arial", 9), bg=PANEL_BG, fg=NORMAL_TEXT)
        self.start_time_label.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        tk.Label(timing_frame, text="⏱️ End Time:", font=("Arial", 9, "bold"), bg=PANEL_BG, fg=SUB_TEXT).grid(row=0, column=2, padx=5, sticky=tk.W)
        self.end_time_label = tk.Label(timing_frame, text="--:-- --", font=("Arial", 9), bg=PANEL_BG, fg=NORMAL_TEXT)
        self.end_time_label.grid(row=0, column=3, padx=5, sticky=tk.W)
        
        # Elapsed time and average time frame
        elapsed_frame = ttk.Frame(progress_frame, style='Panel.TFrame')
        elapsed_frame.grid(row=5, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        elapsed_frame.columnconfigure(1, weight=1)
        elapsed_frame.columnconfigure(3, weight=1)
        
        tk.Label(elapsed_frame, text="⏳ Total Time:", font=("Arial", 9, "bold"), bg=PANEL_BG, fg=SUB_TEXT).grid(row=0, column=0, padx=5, sticky=tk.W)
        self.elapsed_time_label = tk.Label(elapsed_frame, text="--:-- --", font=("Arial", 9), bg=PANEL_BG, fg=NORMAL_TEXT)
        self.elapsed_time_label.grid(row=0, column=1, padx=5, sticky=tk.W)
        
        tk.Label(elapsed_frame, text="⏱️ Avg/Invoice:", font=("Arial", 9, "bold"), bg=PANEL_BG, fg=SUB_TEXT).grid(row=0, column=2, padx=5, sticky=tk.W)
        self.avg_time_label = tk.Label(elapsed_frame, text="-- s", font=("Arial", 9), bg=PANEL_BG, fg=NORMAL_TEXT)
        self.avg_time_label.grid(row=0, column=3, padx=5, sticky=tk.W)
        
        # Log section - fully expandable
        log_frame = ttk.LabelFrame(main_frame, text="Live Logs", padding="10", style='Panel.TLabelframe')
        log_frame.grid(row=(6 if license_frame_created else 5), column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Make log expand with the window; set a reasonable height but allow width to grow
        # Use ScrolledText but configure colors to match theme
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            wrap=tk.WORD,
            font=("Consolas", 9),
            bg=INPUT_BG,
            fg=NORMAL_TEXT,
            bd=0,
            highlightthickness=0,
            insertbackground=NORMAL_TEXT
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Footer with company logo
        footer_frame = ttk.Frame(main_frame)
        footer_frame.grid(row=(7 if license_frame_created else 6), column=0, sticky=(tk.W, tk.E), pady=(5, 0))
        footer_frame.columnconfigure(0, weight=1)
        
        # Try to load and display the company logo
        logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'codium_edge_logo.png')
        if PIL_AVAILABLE and os.path.exists(logo_path):
            try:
                # Load and resize logo
                logo_image = Image.open(logo_path)
                # Resize to appropriate size for footer (height ~40px)
                logo_height = 40
                aspect_ratio = logo_image.width / logo_image.height
                logo_width = int(logo_height * aspect_ratio)
                logo_image = logo_image.resize((logo_width, logo_height), Image.Resampling.LANCZOS)
                self.logo_photo = ImageTk.PhotoImage(logo_image)
                
                # Create logo label
                logo_label = tk.Label(footer_frame, image=self.logo_photo, bg=WINDOW_BG)
                logo_label.grid(row=0, column=0, pady=5)
            except Exception as e:
                logging.warning(f"Could not load logo: {e}")
                # Fallback to text-only footer
                self._create_text_footer(footer_frame)
        else:
            # Fallback to text-only footer
            self._create_text_footer(footer_frame)
        
        # Company name and tagline below logo
        company_label = ttk.Label(
            footer_frame,
            text="◇ Software Provided by Codium Edge ◇",
            style='Normal.TLabel'
        )
        company_label.grid(row=1, column=0, pady=(0, 2))
        
        tagline_label = ttk.Label(
            footer_frame,
            text="Innovating Automation Solutions",
            style='Sub.TLabel'
        )
        tagline_label.grid(row=2, column=0, pady=(0, 5))

        # Style scrollbars inside log_frame (if any) to match theme
        for child in log_frame.winfo_children():
            try:
                if isinstance(child, tk.Scrollbar):
                    child.configure(bg=SCROLLBAR_COLOR, troughcolor=SCROLLBAR_COLOR)
            except Exception:
                pass
    
    def _create_text_footer(self, parent_frame):
        """
        Create a text-based footer when logo is not available.
        
        Args:
            parent_frame: Parent frame to place the footer in
        """
        text_logo = ttk.Label(
            parent_frame,
            text="◇ CODIUM EDGE ◇",
            font=("Arial", 11, "bold"),
            foreground=TITLE_TEXT
        )
        text_logo.grid(row=0, column=0, pady=5)
    
    def show_welcome_message(self):
        """
        Display welcome popup with instructions and license info.
        """
        welcome_text = """
        Welcome to FBR Invoice Checker Bot! 🎉
        
        This tool automates invoice verification on the FBR portal.
        
        📋 How to use:
        
        Step 1: Click 'Browse' to select your Excel file
                (Must contain 'Seller Registration No.' column)
        
        Step 2: Click 'Start' to begin verification
        
        Step 3: Watch the progress and logs in real-time
        
        Step 4: Results will be saved automatically to Excel
        
        Step 5: Review the summary when complete
        
        ⚠️ Important:
        - Chrome browser will open automatically
        - Do not close the browser manually
        - You can pause/resume anytime
        - Results are saved after each invoice
        
        Click OK to continue...
        """
        
        # Add license information if available
        if self.license_manager:
            status = self.license_manager.get_expiry_status()
            license_info = f"\n{'='*60}\n{status['message']}\n{'='*60}"
            welcome_text += license_info
        
        messagebox.showinfo("Welcome", welcome_text)
    
    def browse_file(self):
        """
        Open file dialog to select Excel file.
        """
        file_path = filedialog.askopenfilename(
            title="Select Excel File",
            filetypes=[("Excel Files", "*.xlsx *.xls"), ("All Files", "*.*")]
        )
        
        if file_path:
            self.excel_file_path.set(file_path)
            self.log_message(f"📁 Selected file: {file_path}")
    
    def start_fbr_browser(self):
        """
        Open FBR portal in browser (Start button - just opens browser).
        """
        # Disable start button
        self.start_btn.config(state='disabled')
        self.log_message("🌐 Opening FBR portal...")
        
        # Start browser initialization in a separate thread
        browser_thread = threading.Thread(target=self._initialize_browser_only, daemon=True)
        browser_thread.start()
    
    def _initialize_browser_only(self):
        """
        Worker function to initialize browser and navigate to FBR portal.
        Runs in a separate thread.
        """
        try:
            # Initialize browser
            self.log_message("🌐 Initializing Chrome browser...")
            self.fbr_checker = FBRChecker()
            
            if not self.fbr_checker.initialize_browser():
                self.log_message("❌ Error: Failed to initialize Chrome browser")
                messagebox.showerror("Error", "ChromeDriver not found or failed to initialize.\n\nPlease ensure Chrome browser is installed.")
                self.root.after(0, lambda: self.start_btn.config(state='normal'))
                return
            
            # Navigate to FBR portal
            self.log_message("🔗 Navigating to FBR portal...")
            if not self.fbr_checker.navigate_to_fbr():
                self.log_message("❌ Error: Failed to navigate to FBR portal")
                messagebox.showerror("Error", "Failed to connect to FBR website. Check your internet connection.")
                self.root.after(0, lambda: self.start_btn.config(state='normal'))
                return
            
            self.log_message("✅ FBR portal opened successfully!")
            self.log_message("📝 Please select an Excel file and click 'Verify Invoices' or 'LOAD STWH' to start")
            
            # Enable verify and load stwh buttons after successful browser initialization
            self.root.after(0, lambda: self.verify_btn.config(state='normal'))
            self.root.after(0, lambda: self.load_stwh_btn.config(state='normal'))
            
        except Exception as e:
            self.log_message(f"❌ Error initializing browser: {str(e)}")
            logging.error(f"Browser initialization error: {str(e)}")
            messagebox.showerror("Error", f"Failed to open browser:\n\n{str(e)}")
            self.root.after(0, lambda: self.start_btn.config(state='normal'))
    
    def start_verification(self):
        """
        Start the invoice verification process (Verify Invoices button).
        """
        # Validate file selection
        if not self.excel_file_path.get():
            messagebox.showerror("Error", "Please select an Excel file first!")
            return
        
        # Check if browser is initialized
        if not self.fbr_checker:
            messagebox.showerror("Error", "Please open FBR portal first!")
            return
        
        # Disable verify button, enable pause/stop buttons
        self.verify_btn.config(state='disabled')
        self.pause_btn.grid()  # Show pause button
        self.pause_btn.config(state='normal')
        self.stop_btn.grid()  # Show stop button
        self.stop_btn.config(state='normal')
        
        self.is_running = True
        self.pause_requested = False
        self.current_mode = 'verify'
        
        # Update workflow indicator
        self.root.after(0, lambda: self.workflow_indicator.config(text="▶ Verify Invoices", fg="#27AE60"))
        
        # Reset statistics
        self.processed_count = 0
        self.claimed_count = 0
        self.not_claimed_count = 0
        self.error_count = 0
        
        # Record start time
        self.start_time = time.time()
        self.end_time = None
        start_time_str = time.strftime('%I:%M %p', time.localtime(self.start_time))
        self.root.after(0, lambda: self.start_time_label.config(text=start_time_str))
        self.root.after(0, lambda: self.end_time_label.config(text="--:-- --"))
        
        # Start worker thread for verification
        self.worker_thread = threading.Thread(target=self.verify_invoices, daemon=True)
        self.worker_thread.start()
        
        self.log_message("🚀 Starting invoice verification...")
    
    def start_load_stwh(self):
        """
        Start the LOAD STWH process (similar to verification).
        """
        # Validate file selection
        if not self.excel_file_path.get():
            messagebox.showerror("Error", "Please select an Excel file first!")
            return
        
        # Check if browser is initialized
        if not self.fbr_checker:
            messagebox.showerror("Error", "Please open FBR portal first!")
            return
        
        # Disable load stwh button, enable pause/stop buttons
        self.load_stwh_btn.config(state='disabled')
        self.pause_btn.grid()  # Show pause button
        self.pause_btn.config(state='normal')
        self.stop_btn.grid()  # Show stop button
        self.stop_btn.config(state='normal')
        
        self.is_running = True
        self.pause_requested = False
        self.current_mode = 'stwh'
        
        # Update workflow indicator
        self.root.after(0, lambda: self.workflow_indicator.config(text="📥 LOAD STWH", fg="#3498DB"))
        self.root.after(0, lambda: self.workflow_indicator.config(text="📥 LOAD STWH", fg="#3498DB"))
        
        # Reset statistics
        self.processed_count = 0
        self.claimed_count = 0
        self.not_claimed_count = 0
        self.error_count = 0
        
        # Record start time
        self.start_time = time.time()
        self.end_time = None
        start_time_str = time.strftime('%I:%M %p', time.localtime(self.start_time))
        self.root.after(0, lambda: self.start_time_label.config(text=start_time_str))
        self.root.after(0, lambda: self.end_time_label.config(text="--:-- --"))
        
        # Start worker thread for LOAD STWH
        self.worker_thread = threading.Thread(target=self.load_stwh_process, daemon=True)
        self.worker_thread.start()
        
        self.log_message("🚀 Starting LOAD STWH process...")
    
    def pause_processing(self):
        """
        Pause the invoice verification process.
        """
        self.pause_requested = True
        self.pause_btn.config(state='disabled')
        self.log_message("⏸️ Pause requested... Will pause after current invoice completes")
    
    def resume_processing(self):
        """
        Resume the invoice verification process from where it was paused.
        """
        # Hide resume button, show pause/stop buttons
        self.resume_btn.grid_remove()
        self.pause_btn.grid()
        self.pause_btn.config(state='normal')
        self.stop_btn.grid()
        self.stop_btn.config(state='normal')
        
        self.pause_requested = False
        self.is_running = True
        
        # Determine which process to resume based on current_mode
        if self.current_mode == 'verify':
            self.worker_thread = threading.Thread(target=self.verify_invoices, daemon=True)
            self.log_message("▶️ Resuming invoice verification...")
        elif self.current_mode == 'stwh':
            self.worker_thread = threading.Thread(target=self.load_stwh_process, daemon=True)
            self.log_message("▶️ Resuming LOAD STWH process...")
        else:
            messagebox.showerror("Error", "Unknown processing mode. Please restart.")
            return
        
        self.worker_thread.start()
    
    def stop_processing(self):
        """
        Stop the invoice verification process immediately.
        Saves the Excel file with processed data.
        """
        if messagebox.askyesno("Stop Processing", "Are you sure you want to stop processing?\nThe Excel file will be saved with current progress."):
            self.is_running = False
            self.pause_requested = False
            self.log_message("⏹️ Stop requested... Will stop after current invoice completes")
            
            # Disable stop button to prevent multiple clicks
            self.stop_btn.config(state='disabled')
            self.pause_btn.config(state='disabled')
            
            # Note: Excel will be saved and UI reset by the worker thread's finally block
        else:
            self.log_message("Stop cancelled")
    
    def _show_resume_ui(self):
        """
        Update UI to show resume button after pause.
        """
        self.pause_btn.grid_remove()
        self.stop_btn.grid_remove()
        self.resume_btn.grid()
        self.resume_btn.config(state='normal')
        self.verify_btn.config(state='normal')
        self.load_stwh_btn.config(state='normal')
    
    def _reset_ui_after_stop(self):
        """
        Reset UI after stopping processing.
        """
        self.pause_btn.grid_remove()
        self.stop_btn.grid_remove()
        self.resume_btn.grid_remove()
        self.verify_btn.config(state='normal')
        self.load_stwh_btn.config(state='normal')
        
        # Reset workflow indicator
        if self.workflow_indicator:
            self.workflow_indicator.config(text="None", fg=NORMAL_TEXT)
        
        self.last_processed_row = None
        self.current_mode = None
    
    def verify_invoices(self):
        """
        Main worker function to verify all invoices.
        Runs in a separate thread. Browser should already be initialized.
        """
        import time
        start_time = time.time()  # Track overall start time
        
        try:
            # Initialize Excel handler
            self.log_message("📊 Loading Excel file...")
            self.excel_handler = ExcelHandler(self.excel_file_path.get())
            
            if not self.excel_handler.load_excel():
                self.log_message("❌ Error: Failed to load Excel file")
                messagebox.showerror("Error", "Failed to load Excel file. Check if 'Seller Registration No.' column exists.")
                return
            
            # Get invoice list
            invoices = self.excel_handler.get_invoice_numbers()
            
            if not invoices:
                self.log_message("❌ Error: No invoice numbers found in Excel")
                messagebox.showerror("Error", "No invoice numbers found in the Excel file.")
                return
            
            self.total_invoices = len(invoices)
            self.update_statistics()
            self.log_message(f"📋 Found {self.total_invoices} invoices to verify")
            
            # Determine starting point (resume from last processed row if available)
            start_index = 0
            if self.last_processed_row is not None:
                # Find the index of the row after the last processed one
                for idx, inv in enumerate(invoices):
                    if inv['row_number'] > self.last_processed_row:
                        start_index = idx
                        break
                self.log_message(f"▶️ Resuming from row {self.last_processed_row + 1}")
                self.last_processed_row = None  # Clear after use
            
            # Show column headers for upcoming records
            self.log_message("=" * 80)
            self.log_message("EXCEL COLUMNS: Sr.No | Source | Name | Registration No | Number | Date")
            self.log_message("=" * 80)
            
            # Process each invoice starting from start_index
            
            for invoice_data in invoices[start_index:]:
                invoice_start_time = time.time()  # Track individual invoice start time
                
                # Check if stopped
                if not self.is_running:
                    self.log_message("⏹ Processing stopped by user")
                    break
                
                # Extract data from invoice_data dictionary
                row_number = invoice_data['row']
                sr_no = invoice_data.get('sr_no', 'N/A')
                source_auth = invoice_data.get('source_authority', 'N/A')
                registration_no = invoice_data['seller_registration_no']
                seller_name = invoice_data.get('seller_name', 'N/A')
                number = invoice_data.get('number', 'N/A')
                date = invoice_data.get('date', 'N/A')
                sales_tax_fed_st_mode = invoice_data.get('sales_tax_fed_st_mode', 'N/A')
                
                # Display record details in live logs (table format)
                self.log_message(f"📋 RECORD #{self.processed_count + 1}")
                self.log_message(f"   Row: {row_number} | Sr.No: {sr_no}")
                self.log_message(f"   Source: {source_auth} | Name: {seller_name}")
                self.log_message(f"   Registration No: {registration_no}")
                self.log_message(f"   Number: {number} | Date: {date}")
                self.log_message(f"   Sales Tax/FED in ST Mode: {sales_tax_fed_st_mode}")
                
                # Verify invoice with source authority, invoice number, date, and sales tax from Excel
                self.log_message(f"🔍 Verifying on FBR portal...")
                try:
                    result = self.fbr_checker.verify_invoice(registration_no, source_authority=source_auth, invoice_no_field=number, date_field=date, sales_tax_fed_st_mode=sales_tax_fed_st_mode)
                    
                    # Check if stopped immediately after verification (before updating Excel)
                    if not self.is_running:
                        self.log_message("⏹️ Processing stopped by user")
                        # Save current invoice result before stopping
                        if isinstance(result, dict):
                            status = result.get('status', '⚠️ Error')
                            value_of_purchases = result.get('value_of_purchases', 'N/A')
                            fbr_sales_tax = result.get('fbr_sales_tax', 'N/A')
                        else:
                            status = result
                            value_of_purchases = 'N/A'
                            fbr_sales_tax = 'N/A'
                        self.excel_handler.update_invoice_status(row_number, status, value_of_purchases, fbr_sales_tax)
                        break
                    
                    # Handle both dict and string return types for backwards compatibility
                    if isinstance(result, dict):
                        status = result.get('status', '⚠️ Error')
                        value_of_purchases = result.get('value_of_purchases', 'N/A')
                        fbr_sales_tax = result.get('fbr_sales_tax', 'N/A')
                        
                        # Check if browser was closed by user
                        if 'Browser Closed' in status:
                            self.log_message(f"⚠️ Browser was closed by user. Stopping processing...")
                            self.log_message(f"✅ Progress saved to Excel file up to row {row_number}")
                            break  # Exit the loop gracefully
                    else:
                        # Backwards compatibility: if result is a string
                        status = result
                        value_of_purchases = 'N/A'
                        fbr_sales_tax = 'N/A'
                        
                except Exception as e:
                    # If verify_invoice fails or hangs, catch it and allow loop to continue
                    logging.exception(f"verify_invoice raised exception for row {row_number}: {str(e)}")
                    self.log_message(f"❌ Exception during verification: {str(e)}")
                    status = "⚠️ Error"
                    value_of_purchases = 'N/A'
                    fbr_sales_tax = 'N/A'
                
                # Update Excel with status, value of purchases, and FBR Sales Tax
                self.excel_handler.update_invoice_status(row_number, status, value_of_purchases, fbr_sales_tax)
                
                # Update statistics
                self.processed_count += 1
                
                # Check 'Not Claimed' first because it contains the substring 'Claimed'
                # (e.g. "Not Claimed" contains "Claimed") which would otherwise
                # incorrectly increment the claimed_count.
                if "Not Claimed" in status:
                    self.not_claimed_count += 1
                elif "Claimed" in status:
                    self.claimed_count += 1
                else:
                    self.error_count += 1
                
                self.update_statistics()
                self.update_progress()
                
                self.log_message(f"   ✓ Result: {status}")
                if value_of_purchases and value_of_purchases != 'N/A':
                    self.log_message(f"   💰 Value of Purchases: {value_of_purchases}")
                
                # Calculate and display timing information
                invoice_elapsed_time = time.time() - invoice_start_time
                total_elapsed_time = time.time() - start_time
                average_time_per_invoice = total_elapsed_time / self.processed_count
                
                # Update timing display in GUI
                self.update_timing_display(total_elapsed_time, average_time_per_invoice)
                
                self.log_message(f"   ⏱️ Invoice Time: {invoice_elapsed_time:.1f}s | Total Time: {self._format_time(total_elapsed_time)} | Avg/Invoice: {average_time_per_invoice:.1f}s")
                self.log_message("-" * 80)
                
                # Check for pause request
                if self.pause_requested:
                    self.last_processed_row = row_number
                    self.log_message(f"⏸️ Paused at row {row_number}")
                    self.log_message(f"✅ Progress saved. You can resume later from row {row_number + 1}")
                    
                    # Save and close current state safely
                    if self.excel_handler:
                        try:
                            self.excel_handler.close()
                        except Exception as e:
                            logging.error(f"Error closing Excel on pause: {str(e)}")
                    
                    # Update UI to show resume button
                    self.root.after(0, self._show_resume_ui)
                    return  # Exit the processing loop
                
                # Check if user stopped processing
                if not self.is_running:
                    self.log_message("⏹️ Processing stopped by user")
                    break
                
                # Random delay between requests (human-like behavior)
                delay = random.uniform(0.25, 0.5)
                self.log_message(f"⏱️ Waiting {delay:.1f}s before next invoice...")
                time.sleep(delay)
            
            # Close browser (optional - user can keep it open for manual work)
            # if self.fbr_checker:
            #     self.fbr_checker.close_browser()
            #     self.log_message("🌐 Browser closed")
            
            # Close Excel safely
            if self.excel_handler:
                try:
                    self.excel_handler.close()
                    self.log_message("📊 Excel file saved and closed")
                except Exception as e:
                    logging.error(f"Error closing Excel: {str(e)}")
                    self.log_message(f"⚠️ Warning: Excel close error (data should be saved)")
            
            # Show completion message
            if self.is_running:
                self.show_completion_summary()
            
        except Exception as e:
            self.log_message(f"❌ Critical Error: {str(e)}")
            logging.error(f"Critical error in process_invoices: {str(e)}")
            messagebox.showerror("Critical Error", f"An unexpected error occurred:\n\n{str(e)}")
        
        finally:
            # Cleanup Excel handler - ensure it's saved and closed
            if self.excel_handler:
                try:
                    self.excel_handler.close()
                    logging.info("Excel handler closed successfully in finally block")
                except Exception as close_error:
                    logging.error(f"Error closing Excel in finally block: {str(close_error)}")
            
            # Reset UI (keep browser open)
            self.is_running = False
            self.root.after(0, self._reset_ui_after_stop)
    
    def load_stwh_process(self):
        """
        Main worker function to process LOAD STWH workflow.
        Runs in a separate thread. Browser should already be initialized.
        Replicates the verify_invoices workflow.
        """
        import time
        start_time = time.time()  # Track overall start time
        
        try:
            # Initialize Excel handler
            self.log_message("📊 Loading Excel file for STWH...")
            self.excel_handler = ExcelHandler(self.excel_file_path.get())
            
            if not self.excel_handler.load_excel():
                self.log_message("❌ Error: Failed to load Excel file")
                messagebox.showerror("Error", "Failed to load Excel file. Check if 'Seller Registration No.' column exists.")
                return
            
            # Get invoice list
            invoices = self.excel_handler.get_invoice_numbers()
            
            if not invoices:
                self.log_message("❌ Error: No invoice numbers found in Excel")
                messagebox.showerror("Error", "No invoice numbers found in the Excel file.")
                return
            
            self.total_invoices = len(invoices)
            self.update_statistics()
            self.log_message(f"📋 Found {self.total_invoices} invoices for STWH processing")
            
            # Determine starting point (resume from last processed row if available)
            start_index = 0
            if self.last_processed_row is not None:
                # Find the index of the row after the last processed one
                for idx, inv in enumerate(invoices):
                    if inv['row'] > self.last_processed_row:
                        start_index = idx
                        break
                self.log_message(f"▶️ Resuming from row {self.last_processed_row + 1}")
                self.last_processed_row = None  # Clear after use
            
            # Show column headers for upcoming records
            self.log_message("=" * 80)
            self.log_message("STWH PROCESS: Sr.No | Source | Name | Registration No | Number | Date")
            self.log_message("=" * 80)
            
            # Process each invoice (STWH workflow) starting from start_index
            for invoice_data in invoices[start_index:]:
                invoice_start_time = time.time()  # Track individual invoice start time
                
                # Check if paused
                while self.is_paused and self.is_running:
                    time.sleep(0.5)
                
                # Check if stopped
                if not self.is_running:
                    self.log_message("⏹ STWH processing stopped by user")
                    break
                
                # Extract data from invoice_data dictionary
                row_number = invoice_data['row']
                sr_no = invoice_data.get('sr_no', 'N/A')
                source_auth = invoice_data.get('source_authority', 'N/A')
                registration_no = invoice_data['seller_registration_no']
                seller_name = invoice_data.get('seller_name', 'N/A')
                number = invoice_data.get('number', 'N/A')
                date = invoice_data.get('date', 'N/A')
                sales_tax_fed_st_mode = invoice_data.get('sales_tax_fed_st_mode', 'N/A')
                
                # Display record details in live logs (table format)
                self.log_message(f"📋 STWH RECORD #{self.processed_count + 1}")
                self.log_message(f"   Row: {row_number} | Sr.No: {sr_no}")
                self.log_message(f"   Source: {source_auth} | Name: {seller_name}")
                self.log_message(f"   Registration No: {registration_no}")
                self.log_message(f"   Number: {number} | Date: {date}")
                self.log_message(f"   Sales Tax/FED in ST Mode: {sales_tax_fed_st_mode}")
                
                # Process STWH with source authority, invoice number, date, and sales tax from Excel
                self.log_message(f"🔍 Processing STWH on FBR portal...")
                try:
                    result = self.fbr_checker.load_stwh(registration_no, source_authority=source_auth, invoice_no_field=number, date_field=date, sales_tax_fed_st_mode=sales_tax_fed_st_mode)
                    
                    # Handle both dict and string return types for backwards compatibility
                    if isinstance(result, dict):
                        status = result.get('status', '⚠️ Error')
                        value_of_purchases = result.get('value_of_purchases', 'N/A')
                        fbr_sales_tax = result.get('fbr_sales_tax', 'N/A')
                        
                        # Check if browser was closed by user
                        if 'Browser Closed' in status:
                            self.log_message(f"⚠️ Browser was closed by user. Stopping STWH processing...")
                            self.log_message(f"✅ Progress saved to Excel file up to row {row_number}")
                            break  # Exit the loop gracefully
                    else:
                        # Backwards compatibility: if result is a string
                        status = result
                        value_of_purchases = 'N/A'
                        fbr_sales_tax = 'N/A'
                        
                except Exception as e:
                    # If verify_invoice fails or hangs, catch it and allow loop to continue
                    logging.exception(f"STWH verify_invoice raised exception for row {row_number}: {str(e)}")
                    self.log_message(f"❌ Exception during STWH processing: {str(e)}")
                    status = "⚠️ Error"
                    value_of_purchases = 'N/A'
                    fbr_sales_tax = 'N/A'
                
                # Update Excel with status, value of purchases, and FBR Sales Tax
                self.excel_handler.update_invoice_status(row_number, status, value_of_purchases, fbr_sales_tax)
                
                # Check if user stopped processing (immediate check after STWH processing completes)
                if not self.is_running:
                    self.log_message("⏹️ [STWH] Processing stopped by user")
                    self.log_message(f"✅ Progress saved up to row {row_number}")
                    break
                
                # Update statistics
                self.processed_count += 1
                
                # Check 'Not Claimed' first because it contains the substring 'Claimed'
                if "Not Claimed" in status:
                    self.not_claimed_count += 1
                elif "Claimed" in status:
                    self.claimed_count += 1
                else:
                    self.error_count += 1
                
                self.update_statistics()
                self.update_progress()
                
                self.log_message(f"   ✓ Result: {status}")
                if value_of_purchases and value_of_purchases != 'N/A':
                    self.log_message(f"   💰 Value of Purchases: {value_of_purchases}")
                
                # Calculate and display timing information
                invoice_elapsed_time = time.time() - invoice_start_time
                total_elapsed_time = time.time() - start_time
                average_time_per_invoice = total_elapsed_time / self.processed_count
                
                # Update timing display in GUI
                self.update_timing_display(total_elapsed_time, average_time_per_invoice)
                
                self.log_message(f"   ⏱️ Invoice Time: {invoice_elapsed_time:.1f}s | Total Time: {self._format_time(total_elapsed_time)} | Avg/Invoice: {average_time_per_invoice:.1f}s")
                self.log_message("-" * 80)
                
                # Check for pause request
                if self.pause_requested:
                    self.last_processed_row = row_number
                    self.log_message(f"⏸️ [STWH] Paused at row {row_number}")
                    self.log_message(f"✅ Progress saved. You can resume later from row {row_number + 1}")
                    
                    # Save and close current state safely
                    if self.excel_handler:
                        try:
                            self.excel_handler.close()
                        except Exception as e:
                            logging.error(f"Error closing Excel on pause: {str(e)}")
                    
                    # Update UI to show resume button
                    self.root.after(0, self._show_resume_ui)
                    return  # Exit the processing loop
                
                # Random delay between requests (human-like behavior)
                delay = random.uniform(0.25, 0.5)
                self.log_message(f"⏱️ Waiting {delay:.1f}s before next invoice...")
                time.sleep(delay)
            
            # Close Excel safely
            if self.excel_handler:
                try:
                    self.excel_handler.close()
                    self.log_message("📊 Excel file saved and closed")
                except Exception as e:
                    logging.error(f"Error closing Excel: {str(e)}")
                    self.log_message(f"⚠️ Warning: Excel close error (data should be saved)")
            
            # Show completion message
            if self.is_running:
                self.show_completion_summary()
            
        except Exception as e:
            self.log_message(f"❌ Critical Error in STWH: {str(e)}")
            logging.error(f"Critical error in load_stwh_process: {str(e)}")
            messagebox.showerror("Critical Error", f"An unexpected error occurred:\n\n{str(e)}")
        
        finally:
            # Cleanup Excel handler - ensure it's saved and closed
            if self.excel_handler:
                try:
                    self.excel_handler.close()
                    logging.info("Excel handler closed successfully in finally block")
                except Exception as close_error:
                    logging.error(f"Error closing Excel in finally block: {str(close_error)}")
            
            # Reset UI (keep browser open)
            self.is_running = False
            self.root.after(0, self._reset_ui_after_stop)
    
    def _format_time(self, seconds):
        """
        Format seconds into a human-readable time string (HH:MM:SS).
        
        Args:
            seconds (float): Time in seconds
            
        Returns:
            str: Formatted time string
        """
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m {secs}s"
        elif minutes > 0:
            return f"{minutes}m {secs}s"
        else:
            return f"{secs}s"
    
    def update_statistics(self):
        """
        Update statistics labels in GUI.
        """
        self.root.after(0, lambda: self.total_label.config(text=str(self.total_invoices)))
        self.root.after(0, lambda: self.claimed_label.config(text=str(self.claimed_count)))
        self.root.after(0, lambda: self.not_claimed_label.config(text=str(self.not_claimed_count)))
        self.root.after(0, lambda: self.error_label.config(text=str(self.error_count)))
    
    def update_progress(self):
        """
        Update progress bar and label.
        """
        if self.total_invoices > 0:
            progress_percent = (self.processed_count / self.total_invoices) * 100
            self.root.after(0, lambda: self.progress_bar.config(value=progress_percent))
            self.root.after(0, lambda: self.progress_label.config(
                text=f"Progress: {self.processed_count}/{self.total_invoices} ({progress_percent:.1f}%)"
            ))
    
    def update_timing_display(self, elapsed_time, avg_time_per_invoice):
        """
        Update elapsed time and average time per invoice in GUI.
        
        Args:
            elapsed_time (float): Total elapsed time in seconds
            avg_time_per_invoice (float): Average time per invoice in seconds
        """
        formatted_elapsed = self._format_time(elapsed_time)
        formatted_avg = f"{avg_time_per_invoice:.1f}s"
        self.root.after(0, lambda: self.elapsed_time_label.config(text=formatted_elapsed))
        self.root.after(0, lambda: self.avg_time_label.config(text=formatted_avg))
    
    def log_message(self, message):
        """
        Add a message to the log display.
        
        Args:
            message (str): Message to log
        """
        def append_log():
            self.log_text.insert(tk.END, message + "\n")
            self.log_text.see(tk.END)
        
        self.root.after(0, append_log)
        logging.info(message)
    
    def show_completion_summary(self):
        """
        Show summary popup when processing is complete.
        """
        # Record end time
        self.end_time = time.time()
        end_time_str = time.strftime('%I:%M %p', time.localtime(self.end_time))
        self.root.after(0, lambda: self.end_time_label.config(text=end_time_str))
        
        # Calculate elapsed time
        elapsed_seconds = int(self.end_time - self.start_time) if self.start_time else 0
        hours = elapsed_seconds // 3600
        minutes = (elapsed_seconds % 3600) // 60
        seconds = elapsed_seconds % 60
        elapsed_str = f"{hours}h {minutes}m {seconds}s"
        
        # Calculate average time per invoice
        avg_time_per_invoice = elapsed_seconds / self.processed_count if self.processed_count > 0 else 0
        
        summary_text = f"""
        ✅ Invoice Verification Complete!
        
        📊 Summary:
        
        Total Invoices: {self.total_invoices}
        Processed: {self.processed_count}
        
        ✅ Claimed: {self.claimed_count}
        ❌ Not Claimed: {self.not_claimed_count}
        ⚠️ Errors: {self.error_count}
        
        ⏱️ Time Taken: {elapsed_str}
        ⏱️ Average per Invoice: {avg_time_per_invoice:.1f}s
        
        Results have been saved to:
        {self.excel_file_path.get()}
        
        Check the 'Status' and 'Checked_On' columns in your Excel file.
        """
        
        self.root.after(0, lambda: messagebox.showinfo("Completion Summary", summary_text))
        self.log_message("=" * 80)
        self.log_message("✅ All invoices processed successfully!")
        self.log_message(f"⏱️ Time Taken: {elapsed_str}")
        self.log_message(f"⏱️ Average per Invoice: {avg_time_per_invoice:.1f}s")
    
    # ============================================================================
    # Recording Feature Helper Methods
    # ============================================================================
    
    def start_recording(self):
        """
        Start a new Playwright browser recording session.
        """
        if not PLAYWRIGHT_AVAILABLE:
            messagebox.showerror("Playwright Not Available", "Install Playwright: pip install playwright")
            return
        
        if self.is_recording:
            messagebox.showwarning("Already Recording", "A recording session is already in progress.")
            return
        
        try:
            self.is_recording = True
            self.recorded_steps.clear()
            
            # Update button states
            self.record_btn.config(state='disabled')
            self.stop_record_btn.config(state='normal')
            self.extract_text_btn.config(state='normal')
            
            # Start Playwright in a separate thread
            recording_thread = threading.Thread(target=self._run_playwright_recording, daemon=True)
            recording_thread.start()
            
            self.log_message("🎬 Recording started - Playwright browser opened")
            
        except Exception as e:
            messagebox.showerror("Recording Error", f"Failed to start recording:\n{str(e)}")
            self.log_message(f"❌ Failed to start recording: {str(e)}")
            self.is_recording = False
            self.record_btn.config(state='normal')
    
    def _run_playwright_recording(self):
        """
        Run Playwright in async mode to capture interactions.
        Runs in background thread.
        """
        try:
            asyncio.run(self._async_recording_loop())
        except Exception as e:
            self.log_message(f"❌ Recording loop error: {str(e)}")
            self.is_recording = False
    
    async def _async_recording_loop(self):
        """
        Async loop to capture browser interactions.
        """
        try:
            async with async_playwright() as playwright:
                browser = await playwright.chromium.launch(headless=False)
                self.page = await browser.new_page()
                
                # Set up click listener
                await self.page.add_init_script("""
                    window.__recordedActions__ = [];
                    document.addEventListener('click', async (e) => {
                        const target = e.target;
                        let selector = '';
                        if (target.id) selector = '#' + target.id;
                        else if (target.name) selector = '[name="' + target.name + '"]';
                        else selector = target.tagName.toLowerCase() + '.' + (target.className || '');
                        
                        window.__recordedActions__.push({action: 'click', selector});
                    });
                """)
                
                # Navigate to a default page
                await self.page.goto("about:blank")
                self.log_message("🌐 Playwright browser ready - interact with page to record actions")
                
                # Poll for actions while recording is ON
                while self.is_recording:
                    try:
                        actions = await self.page.evaluate("window.__recordedActions__ || []")
                        
                        # Process new actions
                        for action in actions:
                            if action not in self.recorded_steps:
                                self.append_recorded_step(action)
                        
                        await asyncio.sleep(0.5)
                    except Exception as e:
                        self.log_message(f"⚠️ Polling error: {str(e)}")
                        await asyncio.sleep(1)
                
                # Cleanup
                await browser.close()
                self.log_message("🔌 Playwright browser closed")
                
        except Exception as e:
            self.log_message(f"❌ Async recording error: {str(e)}")
    
    def stop_recording(self):
        """
        Stop the recording session.
        """
        self.is_recording = False
        
        # Update button states
        self.record_btn.config(state='normal')
        self.stop_record_btn.config(state='disabled')
        self.extract_text_btn.config(state='disabled')
        
        self.log_message(f"⏹ Recording stopped ({len(self.recorded_steps)} steps captured)")
    
    def extract_text_mode(self):
        """
        Enable text extraction mode - user can click element to store its text as variable.
        """
        if not self.page:
            messagebox.showwarning("Not Recording", "Start recording first to use text extraction.")
            return
        
        var_name = simpledialog.askstring(
            "Extract Text",
            "Enter variable name to store text as:\n(e.g., invoice_id, status, amount)"
        )
        
        if var_name:
            self.log_message(f"👆 Click on element to extract text as ${{{var_name}}}")
            # In production, would add click listener to page
            # For now, just show log message
    
    def get_selector(self, element_handle):
        """
        Generate a stable CSS selector from an element.
        Priority: #id > [name=""] > tag.class
        
        Args:
            element_handle: Playwright element handle
            
        Returns:
            str: CSS selector
        """
        try:
            # Try to get ID
            element_id = element_handle.get_attribute('id')
            if element_id:
                return f"#{element_id}"
            
            # Try to get name attribute
            name = element_handle.get_attribute('name')
            if name:
                return f'[name="{name}"]'
            
            # Fallback to tag + class
            tag = element_handle.evaluate("e => e.tagName.toLowerCase()")
            class_list = element_handle.evaluate("e => e.className")
            if class_list:
                return f"{tag}.{class_list.split()[0]}"
            
            return tag
        except Exception as e:
            logging.warning(f"Failed to generate selector: {e}")
            return "*"  # Fallback
    
    def append_recorded_step(self, step_dict):
        """
        Append a step to recording and update GUI.
        
        Args:
            step_dict (dict): Step to record (action, selector, value, etc.)
        """
        self.recorded_steps.append(step_dict)
        
        # Update recording display
        step_text = f"{len(self.recorded_steps)}. {step_dict.get('action', 'unknown')}"
        if 'selector' in step_dict:
            step_text += f" → {step_dict['selector']}"
        if 'value' in step_dict:
            step_text += f" ('{step_dict['value']}')"
        if 'store_as' in step_dict:
            step_text += f" → ${{{step_dict['store_as']}}}"
        
        self.log_message(f"🎬 RECORDED: {step_text}")
    
    def save_recording(self):
        """
        Save recorded steps to JSON file.
        """
        if not self.recorded_steps:
            messagebox.showwarning("No Recording", "No steps have been recorded yet.")
            return
        
        try:
            output_file = Path("recorded_steps.json")
            with open(output_file, "w") as f:
                json.dump(self.recorded_steps, f, indent=4)
            
            messagebox.showinfo(
                "Recording Saved",
                f"✅ Recording saved to: {output_file.absolute()}\n\n"
                f"Total steps: {len(self.recorded_steps)}"
            )
            self.log_message(f"💾 Recording saved: {output_file} ({len(self.recorded_steps)} steps)")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save recording:\n{str(e)}")
            self.log_message(f"❌ Failed to save recording: {str(e)}")
    
    def clear_recording(self):
        """
        Clear the current recording.
        """
        if self.recorded_steps:
            if messagebox.askyesno("Clear Recording", "Are you sure? This cannot be undone."):
                self.recorded_steps.clear()
                self.log_message("🗑️ Recording cleared")
    
    def exit_application(self):
        """
        Exit the application.
        """
        if self.is_running:
            if messagebox.askyesno("Confirm Exit", "Processing is in progress. Are you sure you want to exit?"):
                self.is_running = False
                # Clean up resources
                if self.fbr_checker:
                    self.fbr_checker.close_browser()
                if self.excel_handler:
                    self.excel_handler.close()
                # Record end time when exiting
                self.end_time = time.time()
                end_time_str = time.strftime('%I:%M %p', time.localtime(self.end_time))
                self.root.after(0, lambda: self.end_time_label.config(text=end_time_str))
                self.root.destroy()
        else:
            # Clean up resources
            if self.fbr_checker:
                self.fbr_checker.close_browser()
            if self.excel_handler:
                self.excel_handler.close()
            # Record end time even if not processing
            if self.start_time:
                self.end_time = time.time()
                end_time_str = time.strftime('%I:%M %p', time.localtime(self.end_time))
                self.root.after(0, lambda: self.end_time_label.config(text=end_time_str))
            self.root.destroy()
