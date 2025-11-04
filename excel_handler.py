"""
Excel Handler Module
Handles all Excel file operations including reading invoice numbers and updating status.
"""

import openpyxl
from openpyxl import load_workbook, Workbook
import logging
from datetime import datetime


class ExcelHandler:
    """
    Manages Excel file operations for invoice checking.
    Reads invoice numbers and updates their status.
    """
    
    def __init__(self, file_path):
        """
        Initialize the Excel handler with a file path.
        
        Args:
            file_path (str): Path to the Excel file
        """
        self.file_path = file_path
        self.workbook = None
        self.worksheet = None
        self.invoice_column = None
        self.status_column = None
        self.timestamp_column = None
        
    def load_excel(self):
        """
        Load the Excel file and validate required columns.
        
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        try:
            self.workbook = load_workbook(self.file_path)
            self.worksheet = self.workbook.active
            
            # Find the InvoiceNumber column
            headers = [cell.value for cell in self.worksheet[1]]
            
            if 'InvoiceNumber' not in headers:
                logging.error("Column 'InvoiceNumber' not found in Excel file")
                return False
            
            self.invoice_column = headers.index('InvoiceNumber') + 1
            
            # Add Status column if it doesn't exist
            if 'Status' not in headers:
                status_col_idx = len(headers) + 1
                self.worksheet.cell(row=1, column=status_col_idx, value='Status')
                self.status_column = status_col_idx
                logging.info("Added 'Status' column to Excel file")
            else:
                self.status_column = headers.index('Status') + 1
            
            # Add Checked_On column if it doesn't exist
            if 'Checked_On' not in headers:
                timestamp_col_idx = len(headers) + (2 if 'Status' not in headers else 1)
                self.worksheet.cell(row=1, column=timestamp_col_idx, value='Checked_On')
                self.timestamp_column = timestamp_col_idx
                logging.info("Added 'Checked_On' column to Excel file")
            else:
                headers = [cell.value for cell in self.worksheet[1]]  # Refresh headers
                self.timestamp_column = headers.index('Checked_On') + 1
            
            self.workbook.save(self.file_path)
            logging.info(f"Excel file loaded successfully: {self.file_path}")
            return True
            
        except Exception as e:
            logging.error(f"Error loading Excel file: {str(e)}")
            return False
    
    def get_invoice_numbers(self):
        """
        Retrieve all invoice numbers from the Excel file.
        
        Returns:
            list: List of tuples (row_number, invoice_number)
        """
        invoices = []
        
        try:
            # Start from row 2 (skip header)
            for row in range(2, self.worksheet.max_row + 1):
                invoice_number = self.worksheet.cell(row=row, column=self.invoice_column).value
                
                if invoice_number:  # Skip empty cells
                    invoices.append((row, str(invoice_number).strip()))
            
            logging.info(f"Retrieved {len(invoices)} invoice numbers from Excel")
            return invoices
            
        except Exception as e:
            logging.error(f"Error reading invoice numbers: {str(e)}")
            return []
    
    def update_invoice_status(self, row_number, status):
        """
        Update the status of an invoice in the Excel file.
        
        Args:
            row_number (int): Row number in Excel (1-indexed)
            status (str): Status to update (Claimed/Not Claimed/Error)
        """
        try:
            # Update Status column
            self.worksheet.cell(row=row_number, column=self.status_column, value=status)
            
            # Update timestamp
            timestamp = datetime.now().strftime('%Y-%m-%d %I:%M:%S %p')
            self.worksheet.cell(row=row_number, column=self.timestamp_column, value=timestamp)
            
            # Save immediately to prevent data loss
            self.workbook.save(self.file_path)
            
            logging.info(f"Updated row {row_number} with status: {status}")
            
        except Exception as e:
            logging.error(f"Error updating invoice status: {str(e)}")
    
    def close(self):
        """
        Close the Excel workbook.
        """
        try:
            if self.workbook:
                self.workbook.close()
                logging.info("Excel workbook closed")
        except Exception as e:
            logging.error(f"Error closing workbook: {str(e)}")
