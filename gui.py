"""
GUI Module
Interactive Tkinter-based GUI for FBR Invoice Checker Bot.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import logging
from excel_handler import ExcelHandler
from fbr_checker import FBRChecker
from macro_recorder import MacroRecorder, MacroPlayer, MacroLibrary
import time


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
        
        # Macro recording variables
        self.recorder = MacroRecorder()
        self.macro_library = MacroLibrary()
        self.is_recording = False
        self.selected_macro_path = None
        self.use_macro_mode = False
        
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
        
        # Macro controls section
        macro_frame = ttk.LabelFrame(main_frame, text="🎬 Macro Recording & Playback", padding="10")
        macro_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # Row 1: Mode selection
        ttk.Label(macro_frame, text="Mode:").grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.macro_mode_var = tk.StringVar(value="normal")
        ttk.Radiobutton(macro_frame, text="Normal Mode", variable=self.macro_mode_var, 
                       value="normal").grid(row=0, column=1, sticky=tk.W)
        ttk.Radiobutton(macro_frame, text="Macro Mode", variable=self.macro_mode_var, 
                       value="macro").grid(row=0, column=2, sticky=tk.W)
        
        # Row 2: Macro selection
        ttk.Label(macro_frame, text="Macro:").grid(row=1, column=0, sticky=tk.W, padx=(0, 10), pady=(5, 0))
        self.macro_select_combo = ttk.Combobox(macro_frame, state='readonly', width=30)
        self.macro_select_combo.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=(5, 0))
        self.refresh_macro_list()
        
        ttk.Button(macro_frame, text="⟳ Refresh", command=self.refresh_macro_list, 
                  width=10).grid(row=1, column=3, padx=(5, 0), pady=(5, 0))
        
        # Row 3: Macro action buttons
        macro_btn_frame = ttk.Frame(macro_frame)
        macro_btn_frame.grid(row=2, column=0, columnspan=4, pady=(10, 0))
        
        self.record_btn = ttk.Button(
            macro_btn_frame,
            text="⏺ Record",
            command=self.start_recording,
            width=12
        )
        self.record_btn.grid(row=0, column=0, padx=3)
        
        self.stop_record_btn = ttk.Button(
            macro_btn_frame,
            text="⏹ Stop",
            command=self.stop_recording,
            width=12,
            state='disabled'
        )
        self.stop_record_btn.grid(row=0, column=1, padx=3)
        
        ttk.Button(
            macro_btn_frame,
            text="📂 Load",
            command=self.load_macro,
            width=12
        ).grid(row=0, column=2, padx=3)
        
        ttk.Button(
            macro_btn_frame,
            text="✏️ Edit",
            command=self.edit_macro,
            width=12
        ).grid(row=0, column=3, padx=3)
        
        ttk.Button(
            macro_btn_frame,
            text="🗑️ Delete",
            command=self.delete_macro,
            width=12
        ).grid(row=0, column=4, padx=3)
        
        macro_frame.columnconfigure(1, weight=1)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=3, pady=(0, 15))
        
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
                (Must contain 'InvoiceNumber' column)
        
        Step 2: Choose Normal Mode or Macro Mode
                - Normal Mode: Standard automated verification
                - Macro Mode: Use recorded workflows
        
        Step 3: Click 'Start' to begin verification
        
        Step 4: Watch the progress and logs in real-time
        
        Step 5: Results will be saved automatically to Excel
        
        🎬 Macro Features:
        - Record: Record your workflow for reuse
        - Load: Import existing macros
        - Edit: Modify macro JSON files
        - Delete: Remove unwanted macros
        
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
        macro_player = None
        
        try:
            # Initialize Excel handler
            self.log_message("📊 Loading Excel file...")
            excel_handler = ExcelHandler(self.excel_file_path.get())
            
            if not excel_handler.load_excel():
                self.log_message("❌ Error: Failed to load Excel file")
                messagebox.showerror("Error", "Failed to load Excel file. Check if 'InvoiceNumber' column exists.")
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
            
            # Check if macro mode is enabled
            use_macro = self.macro_mode_var.get() == "macro"
            selected_macro = self.macro_select_combo.get()
            
            if use_macro and not selected_macro:
                self.log_message("❌ Error: Macro mode enabled but no macro selected")
                messagebox.showerror("Error", "Please select a macro or switch to Normal Mode.")
                return
            
            # Initialize browser
            self.log_message("🌐 Initializing Chrome browser...")
            
            # Pass recorder to FBRChecker if recording
            recorder_to_use = self.recorder if self.is_recording else None
            fbr_checker = FBRChecker(recorder=recorder_to_use)
            
            if not fbr_checker.initialize_browser():
                self.log_message("❌ Error: Failed to initialize Chrome browser")
                messagebox.showerror("Error", "ChromeDriver not found or failed to initialize.\n\nPlease ensure Chrome browser is installed.")
                return
            
            # Initialize macro player if macro mode
            if use_macro:
                self.log_message(f"🎬 Loading macro: {selected_macro}")
                macro_path = self.macro_library.get_macro_path(selected_macro)
                
                temp_recorder = MacroRecorder()
                if not temp_recorder.load(macro_path):
                    self.log_message("❌ Error: Failed to load macro")
                    messagebox.showerror("Error", f"Failed to load macro: {selected_macro}")
                    return
                
                macro_player = MacroPlayer(fbr_checker.driver, logger=self.log_message)
                macro_actions = temp_recorder.get_actions()
                self.log_message(f"✅ Loaded macro with {len(macro_actions)} actions")
            else:
                # Navigate to FBR portal in normal mode
                self.log_message("🔗 Navigating to FBR portal...")
                if not fbr_checker.navigate_to_fbr():
                    self.log_message("❌ Error: Failed to navigate to FBR portal")
                    messagebox.showerror("Error", "Failed to connect to FBR website. Check your internet connection.")
                    return
                
                self.log_message("✅ Connected to FBR portal successfully")
            
            self.log_message("=" * 80)
            
            # Process each invoice
            for row_number, invoice_number in invoices:
                # Check if paused
                while self.is_paused and self.is_running:
                    time.sleep(0.5)
                
                # Check if stopped
                if not self.is_running:
                    self.log_message("⏹ Processing stopped by user")
                    break
                
                self.log_message(f"🔍 Checking invoice: {invoice_number}...")
                
                if use_macro:
                    # Use macro playback
                    context = {
                        "invoice_number": str(invoice_number),
                        "row_number": str(row_number)
                    }
                    
                    try:
                        result = macro_player.play(macro_actions, context=context, step_delay=0.5)
                        
                        if result["success"]:
                            # Try to determine status from page
                            page_source = fbr_checker.driver.page_source.lower()
                            
                            if "no records found" in page_source or "no record found" in page_source:
                                status = "❌ Not Claimed"
                            elif "record" in page_source or str(invoice_number) in page_source:
                                status = "✅ Claimed"
                            else:
                                status = "✅ Checked (Macro)"
                        else:
                            status = f"⚠️ Error - Macro failed ({result['failed_actions']} actions)"
                        
                    except Exception as e:
                        self.log_message(f"   ❌ Macro error: {str(e)}")
                        status = "⚠️ Error - Macro exception"
                else:
                    # Use normal verification
                    status = fbr_checker.verify_invoice(invoice_number)
                
                # Update Excel
                excel_handler.update_invoice_status(row_number, status)
                
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
                
                self.log_message(f"   → Result: {status}")
                self.log_message("-" * 80)
                
                # Small delay between requests
                time.sleep(1)
            
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
    
    def refresh_macro_list(self):
        """
        Refresh the list of available macros in the combobox.
        """
        macros = self.macro_library.list_macros()
        macro_names = [m['name'] for m in macros]
        
        self.macro_select_combo['values'] = macro_names
        
        if macro_names and not self.macro_select_combo.get():
            self.macro_select_combo.current(0)
    
    def start_recording(self):
        """
        Start recording a new macro.
        """
        # Ask for macro name
        name_dialog = tk.Toplevel(self.root)
        name_dialog.title("New Macro")
        name_dialog.geometry("400x150")
        name_dialog.transient(self.root)
        name_dialog.grab_set()
        
        ttk.Label(name_dialog, text="Enter a name for the new macro:", 
                 font=("Arial", 10)).pack(pady=(20, 10))
        
        name_var = tk.StringVar(value="my_macro")
        name_entry = ttk.Entry(name_dialog, textvariable=name_var, width=40)
        name_entry.pack(pady=10)
        name_entry.focus()
        
        def on_ok():
            macro_name = name_var.get().strip()
            if not macro_name:
                messagebox.showerror("Error", "Please enter a macro name!")
                return
            
            self.recorder.start(macro_name)
            self.is_recording = True
            self.record_btn.config(state='disabled')
            self.stop_record_btn.config(state='normal')
            self.log_message(f"🔴 Started recording macro: {macro_name}")
            name_dialog.destroy()
        
        def on_cancel():
            name_dialog.destroy()
        
        btn_frame = ttk.Frame(name_dialog)
        btn_frame.pack(pady=10)
        
        ttk.Button(btn_frame, text="OK", command=on_ok, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Cancel", command=on_cancel, width=10).pack(side=tk.LEFT, padx=5)
        
        name_entry.bind('<Return>', lambda e: on_ok())
    
    def stop_recording(self):
        """
        Stop recording the current macro and save it.
        """
        if not self.is_recording:
            return
        
        action_count = self.recorder.stop()
        self.is_recording = False
        
        # Ask user to save
        if messagebox.askyesno("Save Macro", 
                               f"Recording stopped ({action_count} actions).\n\nDo you want to save this macro?"):
            try:
                macro_path = self.macro_library.get_macro_path(self.recorder.macro_name)
                self.recorder.save(macro_path, metadata={"source": "GUI Recording"})
                self.log_message(f"💾 Macro saved: {self.recorder.macro_name}")
                self.refresh_macro_list()
                
                # Select the newly saved macro
                self.macro_select_combo.set(self.recorder.macro_name)
            except Exception as e:
                self.log_message(f"❌ Error saving macro: {str(e)}")
                messagebox.showerror("Error", f"Failed to save macro:\n{str(e)}")
        else:
            self.log_message("⚠️ Macro discarded")
        
        self.record_btn.config(state='normal')
        self.stop_record_btn.config(state='disabled')
    
    def load_macro(self):
        """
        Load a macro from file.
        """
        file_path = filedialog.askopenfilename(
            title="Load Macro",
            filetypes=[("JSON Files", "*.json"), ("All Files", "*.*")],
            initialdir="macros"
        )
        
        if file_path:
            if self.recorder.load(file_path):
                self.log_message(f"📂 Loaded macro: {self.recorder.macro_name}")
                self.refresh_macro_list()
                self.macro_select_combo.set(self.recorder.macro_name)
            else:
                messagebox.showerror("Error", "Failed to load macro file!")
    
    def edit_macro(self):
        """
        Open macro editor dialog.
        """
        selected = self.macro_select_combo.get()
        
        if not selected:
            messagebox.showinfo("Info", "Please select a macro to edit")
            return
        
        macro_path = self.macro_library.get_macro_path(selected)
        
        try:
            import json
            with open(macro_path, 'r', encoding='utf-8') as f:
                macro_content = f.read()
            
            # Create editor dialog
            editor = tk.Toplevel(self.root)
            editor.title(f"Edit Macro: {selected}")
            editor.geometry("800x600")
            
            ttk.Label(editor, text=f"Editing: {selected}", 
                     font=("Arial", 12, "bold")).pack(pady=10)
            
            # Text editor
            text_frame = ttk.Frame(editor)
            text_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
            
            text_editor = scrolledtext.ScrolledText(text_frame, wrap=tk.WORD, 
                                                    font=("Consolas", 10))
            text_editor.pack(fill=tk.BOTH, expand=True)
            text_editor.insert(1.0, macro_content)
            
            # Buttons
            btn_frame = ttk.Frame(editor)
            btn_frame.pack(pady=10)
            
            def save_changes():
                try:
                    new_content = text_editor.get(1.0, tk.END)
                    # Validate JSON
                    json.loads(new_content)
                    
                    with open(macro_path, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    
                    self.log_message(f"✅ Macro updated: {selected}")
                    messagebox.showinfo("Success", "Macro saved successfully!")
                    editor.destroy()
                except json.JSONDecodeError as e:
                    messagebox.showerror("JSON Error", f"Invalid JSON format:\n{str(e)}")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save macro:\n{str(e)}")
            
            ttk.Button(btn_frame, text="💾 Save", command=save_changes, width=12).pack(side=tk.LEFT, padx=5)
            ttk.Button(btn_frame, text="✖ Cancel", command=editor.destroy, width=12).pack(side=tk.LEFT, padx=5)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open macro:\n{str(e)}")
    
    def delete_macro(self):
        """
        Delete the selected macro.
        """
        selected = self.macro_select_combo.get()
        
        if not selected:
            messagebox.showinfo("Info", "Please select a macro to delete")
            return
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete macro:\n\n{selected}?"):
            if self.macro_library.delete_macro(selected):
                self.log_message(f"🗑️ Deleted macro: {selected}")
                self.refresh_macro_list()
            else:
                messagebox.showerror("Error", "Failed to delete macro!")
    
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
