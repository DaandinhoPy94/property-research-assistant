# debug_sheets.py - Debug Google Sheets connection
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'api'))

from sheets_connector import sheets_manager

def debug_sheets():
    """Debug Google Sheets connection step by step"""
    
    print("🔍 Debugging Google Sheets connection...")
    
    # Check if connected
    print(f"Connected: {sheets_manager.client is not None}")
    print(f"Spreadsheet: {sheets_manager.spreadsheet is not None}")
    
    if sheets_manager.spreadsheet:
        print(f"Spreadsheet title: {sheets_manager.spreadsheet.title}")
        print(f"Spreadsheet ID: {sheets_manager.spreadsheet.id}")
        
        try:
            # Get worksheet
            worksheet = sheets_manager.spreadsheet.sheet1
            print(f"Worksheet found: {worksheet.title}")
            
            # Get all values
            all_values = worksheet.get_all_values()
            print(f"Total rows: {len(all_values)}")
            
            if len(all_values) > 0:
                print(f"First row: {all_values[0]}")
                if len(all_values) > 1:
                    print(f"Second row: {all_values[1]}")
            else:
                print("No data in spreadsheet!")
            
            # Try get_all_records
            try:
                records = worksheet.get_all_records()
                print(f"Records found: {len(records)}")
                if records:
                    print(f"First record keys: {list(records[0].keys())}")
            except Exception as e:
                print(f"get_all_records failed: {e}")
            
        except Exception as e:
            print(f"Error accessing worksheet: {e}")
    
    else:
        print("No spreadsheet connected!")

if __name__ == "__main__":
    debug_sheets()