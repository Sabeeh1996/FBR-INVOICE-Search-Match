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
    
    def __init__(self, root):
        """
        Initialize the GUI application.
        
        Args:
            root: Tkinter root window
        """
        self.root = root
        self.root.title("🧾 FBR Invoice Checker Bot")
        # Start with a reasonable default size but allow resizing for responsiveness
        self.root.geometry("900x650")
        self.root.minsize(720, 480)
        self.root.resizable(True, True)
        
        # Variables
        self.excel_file_path = tk.StringVar()
        self.is_running = False
        self.is_paused = False
        self.worker_thread = None
        
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
        
        # Setup GUI
        self.setup_gui()
        
        # Show welcome message
        self.show_welcome_message()
    
    def setup_gui(self):
        """
        Setup all GUI components.
        """
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Title
        title_label = ttk.Label(
            main_frame, 
            text="🧾 FBR Invoice Checker Bot", 
            font=("Arial", 18, "bold")
        )
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # File selection section
        file_frame = ttk.LabelFrame(main_frame, text="Excel File Selection", padding="10")
        file_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(file_frame, text="Excel File:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        file_entry = ttk.Entry(file_frame, textvariable=self.excel_file_path, state='readonly')
        file_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        browse_btn = ttk.Button(file_frame, text="Browse...", command=self.browse_file)
        browse_btn.grid(row=0, column=2)
        
        file_frame.columnconfigure(1, weight=1)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=2, column=0, columnspan=3, pady=(0, 15))
        
        self.start_btn = ttk.Button(
            button_frame, 
            text="▶ Start", 
            command=self.start_processing,
            width=12
        )
        self.start_btn.grid(row=0, column=0, padx=5)
        
        self.pause_btn = ttk.Button(
            button_frame, 
            text="⏸ Pause", 
            command=self.pause_processing,
            width=12,
            state='disabled'
        )
        self.pause_btn.grid(row=0, column=1, padx=5)
        
        self.resume_btn = ttk.Button(
            button_frame, 
            text="▶ Resume", 
            command=self.resume_processing,
            width=12,
            state='disabled'
        )
        self.resume_btn.grid(row=0, column=2, padx=5)
        
        self.exit_btn = ttk.Button(
            button_frame, 
            text="✖ Exit", 
            command=self.exit_application,
            width=12
        )
        self.exit_btn.grid(row=0, column=3, padx=5)
        
        # Recording controls have been removed from the UI
        
        # Progress section
        progress_frame = ttk.LabelFrame(main_frame, text="Progress", padding="10")
        progress_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Let progress bar expand horizontally with the window
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            mode='determinate'
        )
        self.progress_bar.grid(row=0, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Progress label
        self.progress_label = ttk.Label(progress_frame, text="Ready to start", font=("Arial", 10))
        self.progress_label.grid(row=1, column=0, columnspan=4, pady=(0, 10))
        
        # Statistics
        stats_frame = ttk.Frame(progress_frame)
        stats_frame.grid(row=2, column=0, columnspan=4)
        
        ttk.Label(stats_frame, text="Total:", font=("Arial", 9, "bold")).grid(row=0, column=0, padx=5)
        self.total_label = ttk.Label(stats_frame, text="0", font=("Arial", 9))
        self.total_label.grid(row=0, column=1, padx=5)
        
        ttk.Label(stats_frame, text="✅ Claimed:", font=("Arial", 9, "bold"), foreground="green").grid(row=0, column=2, padx=5)
        self.claimed_label = ttk.Label(stats_frame, text="0", font=("Arial", 9))
        self.claimed_label.grid(row=0, column=3, padx=5)
        
        ttk.Label(stats_frame, text="❌ Not Claimed:", font=("Arial", 9, "bold"), foreground="red").grid(row=0, column=4, padx=5)
        self.not_claimed_label = ttk.Label(stats_frame, text="0", font=("Arial", 9))
        self.not_claimed_label.grid(row=0, column=5, padx=5)
        
        ttk.Label(stats_frame, text="⚠️ Errors:", font=("Arial", 9, "bold"), foreground="orange").grid(row=0, column=6, padx=5)
        self.error_label = ttk.Label(stats_frame, text="0", font=("Arial", 9))
        self.error_label.grid(row=0, column=7, padx=5)
        
        progress_frame.columnconfigure(0, weight=1)
        
        # Log section
        log_frame = ttk.LabelFrame(main_frame, text="Live Logs", padding="10")
        log_frame.grid(row=4, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Make log expand with the window; set a reasonable height but allow width to grow
        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            height=15,
            wrap=tk.WORD,
            font=("Consolas", 9)
        )
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        
        # Configure main frame to expand
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.columnconfigure(2, weight=1)
        main_frame.rowconfigure(4, weight=1)
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
    
    def show_welcome_message(self):
        """
        Display welcome popup with instructions.
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
    
    def start_processing(self):
        """
        Start the invoice verification process.
        """
        # Validate file selection
        if not self.excel_file_path.get():
            messagebox.showerror("Error", "Please select an Excel file first!")
            return
        
        # Disable start button
        self.start_btn.config(state='disabled')
        self.pause_btn.config(state='normal')
        self.is_running = True
        
        # Reset statistics
        self.processed_count = 0
        self.claimed_count = 0
        self.not_claimed_count = 0
        self.error_count = 0
        
        # Clear log
        self.log_text.delete(1.0, tk.END)
        
        # Start worker thread
        self.worker_thread = threading.Thread(target=self.process_invoices, daemon=True)
        self.worker_thread.start()
        
        self.log_message("🚀 Starting invoice verification...")
    
    def pause_processing(self):
        """
        Pause the invoice verification process.
        """
        self.is_paused = True
        self.pause_btn.config(state='disabled')
        self.resume_btn.config(state='normal')
        self.log_message("⏸ Processing paused")
    
    def resume_processing(self):
        """
        Resume the invoice verification process.
        """
        self.is_paused = False
        self.pause_btn.config(state='normal')
        self.resume_btn.config(state='disabled')
        self.log_message("▶ Processing resumed")
    
    def process_invoices(self):
        """
        Main worker function to process all invoices.
        Runs in a separate thread.
        """
        excel_handler = None
        fbr_checker = None
        
        try:
            # Initialize Excel handler
            self.log_message("📊 Loading Excel file...")
            excel_handler = ExcelHandler(self.excel_file_path.get())
            
            if not excel_handler.load_excel():
                self.log_message("❌ Error: Failed to load Excel file")
                messagebox.showerror("Error", "Failed to load Excel file. Check if 'Seller Registration No.' column exists.")
                return
            
            # Get invoice list
            invoices = excel_handler.get_invoice_numbers()
            
            if not invoices:
                self.log_message("❌ Error: No invoice numbers found in Excel")
                messagebox.showerror("Error", "No invoice numbers found in the Excel file.")
                return
            
            self.total_invoices = len(invoices)
            self.update_statistics()
            self.log_message(f"📋 Found {self.total_invoices} invoices to verify")
            
            # Show column headers for upcoming records
            self.log_message("=" * 80)
            self.log_message("EXCEL COLUMNS: Sr.No | Source | Name | Registration No | Number | Date")
            self.log_message("=" * 80)
            
            # Initialize browser
            self.log_message("🌐 Initializing Chrome browser...")
            fbr_checker = FBRChecker()
            
            if not fbr_checker.initialize_browser():
                self.log_message("❌ Error: Failed to initialize Chrome browser")
                messagebox.showerror("Error", "ChromeDriver not found or failed to initialize.\n\nPlease ensure Chrome browser is installed.")
                return
            
            # Navigate to FBR portal
            self.log_message("🔗 Navigating to FBR portal...")
            if not fbr_checker.navigate_to_fbr():
                self.log_message("❌ Error: Failed to navigate to FBR portal")
                messagebox.showerror("Error", "Failed to connect to FBR website. Check your internet connection.")
                return
            
            self.log_message("✅ Connected to FBR portal successfully")
            self.log_message("=" * 80)
            
            # Process each invoice
            
            for invoice_data in invoices:
                # Check if paused
                while self.is_paused and self.is_running:
                    time.sleep(0.5)
                
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
                
                # Display record details in live logs (table format)
                self.log_message(f"� RECORD #{self.processed_count + 1}")
                self.log_message(f"   Row: {row_number} | Sr.No: {sr_no}")
                self.log_message(f"   Source: {source_auth} | Name: {seller_name}")
                self.log_message(f"   Registration No: {registration_no}")
                self.log_message(f"   Number: {number} | Date: {date}")
                
                # Verify invoice with source authority, invoice number, and date from Excel
                self.log_message(f"🔍 Verifying on FBR portal...")
                try:
                    status = fbr_checker.verify_invoice(registration_no, source_authority=source_auth, invoice_no_field=number, date_field=date)
                except Exception as e:
                    # If verify_invoice fails or hangs, catch it and allow loop to continue
                    logging.exception(f"verify_invoice raised exception for row {row_number}: {str(e)}")
                    self.log_message(f"❌ Exception during verification: {str(e)}")
                    status = "⚠️ Error"
                
                # Update Excel
                excel_handler.update_invoice_status(row_number, status)
                
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
                self.log_message("-" * 80)
                
                # Random delay between requests (human-like behavior)
                delay = random.uniform(2.0, 5.0)
                self.log_message(f"⏱️ Waiting {delay:.1f}s before next invoice...")
                time.sleep(delay)
            
            # Close browser
            if fbr_checker:
                fbr_checker.close_browser()
                self.log_message("🌐 Browser closed")
            
            # Close Excel
            if excel_handler:
                excel_handler.close()
                self.log_message("📊 Excel file saved and closed")
            
            # Show completion message
            if self.is_running:
                self.show_completion_summary()
            
        except Exception as e:
            self.log_message(f"❌ Critical Error: {str(e)}")
            logging.error(f"Critical error in process_invoices: {str(e)}")
            messagebox.showerror("Critical Error", f"An unexpected error occurred:\n\n{str(e)}")
        
        finally:
            # Cleanup
            if fbr_checker:
                fbr_checker.close_browser()
            if excel_handler:
                excel_handler.close()
            
            # Reset UI
            self.is_running = False
            self.start_btn.config(state='normal')
            self.pause_btn.config(state='disabled')
            self.resume_btn.config(state='disabled')
    
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
        summary_text = f"""
        ✅ Invoice Verification Complete!
        
        📊 Summary:
        
        Total Invoices: {self.total_invoices}
        Processed: {self.processed_count}
        
        ✅ Claimed: {self.claimed_count}
        ❌ Not Claimed: {self.not_claimed_count}
        ⚠️ Errors: {self.error_count}
        
        Results have been saved to:
        {self.excel_file_path.get()}
        
        Check the 'Status' and 'Checked_On' columns in your Excel file.
        """
        
        self.root.after(0, lambda: messagebox.showinfo("Completion Summary", summary_text))
        self.log_message("=" * 80)
        self.log_message("✅ All invoices processed successfully!")
    
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
                self.root.destroy()
        else:
            self.root.destroy()
