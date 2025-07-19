# api/sheets_connector.py
import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
from datetime import datetime
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv

load_dotenv()

class PropertySheetsManager:
    """
    Manages Google Sheets integration for property research data
    """
    
    def __init__(self):
        self.credentials_path = os.getenv("GOOGLE_SHEETS_CREDENTIALS_PATH", "credentials.json")
        self.spreadsheet_id = os.getenv("GOOGLE_SHEETS_SPREADSHEET_ID")
        
        # Google Sheets scopes
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        
        self.client = None
        self.spreadsheet = None
        
        # Initialize connection
        self._connect()
    
    def _connect(self):
        """
        Establish connection to Google Sheets
        """
        try:
            # Load credentials
            if not os.path.exists(self.credentials_path):
                print(f"⚠️ Credentials file not found: {self.credentials_path}")
                return False
            
            creds = Credentials.from_service_account_file(
                self.credentials_path, 
                scopes=self.scopes
            )
            
            # Create client
            self.client = gspread.authorize(creds)
            
            # Open spreadsheet if ID provided
            if self.spreadsheet_id:
                self.spreadsheet = self.client.open_by_key(self.spreadsheet_id)
                print(f"✅ Connected to Google Sheets: {self.spreadsheet.title}")
            else:
                print("⚠️ No spreadsheet ID provided - will create new one")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to connect to Google Sheets: {str(e)}")
            return False
    
    def create_property_database(self, sheet_name: str = "Property Research Database"):
        """
        Create a new spreadsheet with proper structure for property research
        """
        try:
            # Create new spreadsheet
            self.spreadsheet = self.client.create(sheet_name)
            
            # Share with your email (replace with actual email)
            self.spreadsheet.share('daanvdster@gmail.com', perm_type='user', role='owner')
            
            # Get the main worksheet
            worksheet = self.spreadsheet.sheet1
            
            # Set up headers
            headers = [
                'ID', 'Date_Added', 'Property_Address', 'City', 'Postal_Code',
                'Property_Type', 'Asking_Price', 'Size_m2', 'Bedrooms', 
                'Status', 'Market_Score', 'AI_Grade', 'AI_Summary', 
                'Investment_Recommendation', 'Processing_Time', 'Last_Updated',
                'Research_Report_URL', 'Email_Notification'
            ]
            
            # Add headers to first row
            worksheet.update('A1:R1', [headers])
            
            # Format headers (bold)
            worksheet.format('A1:R1', {
                'textFormat': {'bold': True},
                'backgroundColor': {'red': 0.9, 'green': 0.9, 'blue': 0.9}
            })
            
            # Set column widths
            worksheet.update('A2:R2', [[''] * len(headers)])  # Add empty row for better formatting
            
            print(f"✅ Created new spreadsheet: {self.spreadsheet.title}")
            print(f"📋 Spreadsheet ID: {self.spreadsheet.id}")
            print(f"🔗 URL: https://docs.google.com/spreadsheets/d/{self.spreadsheet.id}")
            
            return self.spreadsheet.id
            
        except Exception as e:
            print(f"❌ Failed to create spreadsheet: {str(e)}")
            return None
    
    def add_property(self, property_data: Dict, analysis_result: Dict) -> bool:
        """
        Add a new property to the spreadsheet
        """
        try:
            if not self.spreadsheet:
                print("❌ No spreadsheet connected")
                return False
            
            worksheet = self.spreadsheet.sheet1
            
            # Get next available row
            next_row = len(worksheet.get_all_values()) + 1
            
            # Prepare data row
            ai_analysis = analysis_result.get('analysis', {}).get('ai_analysis', {})
            
            row_data = [
                next_row - 1,  # ID (row number - 1 for header)
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Date_Added
                property_data.get('address', ''),  # Property_Address
                property_data.get('city', ''),  # City
                property_data.get('postal_code', ''),  # Postal_Code
                property_data.get('property_type', ''),  # Property_Type
                property_data.get('asking_price', 0),  # Asking_Price
                property_data.get('size_m2', 0),  # Size_m2
                property_data.get('bedrooms', 'N/A'),  # Bedrooms
                'New',  # Status
                analysis_result.get('analysis', {}).get('market_score', 0),  # Market_Score
                ai_analysis.get('investment_grade', 'N/A'),  # AI_Grade
                ai_analysis.get('executive_summary', 'N/A')[:200] + '...',  # AI_Summary (truncated)
                ai_analysis.get('bottom_line', 'N/A'),  # Investment_Recommendation
                analysis_result.get('processing_time_seconds', 0),  # Processing_Time
                datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # Last_Updated
                '',  # Research_Report_URL (to be filled later)
                property_data.get('email_notification', '')  # Email_Notification
            ]
            
            # Add row to spreadsheet
            worksheet.update(f'A{next_row}:R{next_row}', [row_data])
            
            print(f"✅ Added property to row {next_row}: {property_data.get('address')}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to add property: {str(e)}")
            return False
    
    def get_new_properties(self) -> List[Dict]:
        """
        Get all properties with status 'New' for processing
        """
        try:
            if not self.spreadsheet:
                print("❌ No spreadsheet connected")
                return []
            
            worksheet = self.spreadsheet.sheet1
            records = worksheet.get_all_records()
            
            # Filter for new properties
            new_properties = [
                record for record in records 
                if record.get('Status', '').strip().lower() == 'new'
            ]
            
            print(f"📋 Found {len(new_properties)} new properties to process")
            
            return new_properties
            
        except Exception as e:
            print(f"❌ Failed to get new properties: {str(e)}")
            return []
    
    def update_property_status(self, property_id: int, status: str, additional_data: Dict = None):
        """
        Update property status and additional data
        """
        try:
            if not self.spreadsheet:
                print("❌ No spreadsheet connected")
                return False
            
            worksheet = self.spreadsheet.sheet1
            
            # Find the row with matching ID
            row_num = property_id + 2  # +1 for header, +1 for 0-based indexing
            
            # Update status
            worksheet.update(f'J{row_num}', status)  # Status is column J
            
            # Update timestamp
            worksheet.update(f'P{row_num}', datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
            
            # Update additional data if provided
            if additional_data:
                if 'research_report_url' in additional_data:
                    worksheet.update(f'Q{row_num}', additional_data['research_report_url'])
            
            print(f"✅ Updated property {property_id} status to: {status}")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to update property status: {str(e)}")
            return False
    
    def get_spreadsheet_info(self) -> Dict:
        """
        Get basic information about the connected spreadsheet
        """
        if not self.spreadsheet:
            return {"connected": False, "error": "No spreadsheet connected"}
        
        try:
            worksheet = self.spreadsheet.sheet1
            
            # Safer way to get records
            all_values = worksheet.get_all_values()
            
            if len(all_values) <= 1:  # Only headers or empty
                records = []
            else:
                try:
                    records = worksheet.get_all_records()
                except Exception:
                    records = []
            
            return {
                "connected": True,
                "title": self.spreadsheet.title,
                "id": self.spreadsheet.id,
                "url": f"https://docs.google.com/spreadsheets/d/{self.spreadsheet.id}",
                "total_rows": len(all_values),
                "total_properties": len(records),
                "new_properties": len([r for r in records if r.get('Status', '').lower() == 'new']),
                "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
        except Exception as e:
            print(f"❌ Failed to get spreadsheet info: {str(e)}")
            return {"connected": False, "error": str(e)}
    
    def create_sample_data(self):
        """
        Add sample property data for testing
        """
        sample_properties = [
            {
                "address": "Damrak 70",
                "city": "Amsterdam", 
                "postal_code": "1012LM",
                "property_type": "apartment",
                "asking_price": 425000,
                "size_m2": 75,
                "email_notification": "daanvdster@gmail.com"
            },
            {
                "address": "Coolsingel 31",
                "city": "Rotterdam",
                "postal_code": "3011AD", 
                "property_type": "apartment",
                "asking_price": 285000,
                "size_m2": 68,
                "email_notification": "daanvdster@gmail.com"
            },
            {
                "address": "Oudegracht 99",
                "city": "Utrecht",
                "postal_code": "3511AE",
                "property_type": "house", 
                "asking_price": 395000,
                "size_m2": 95,
                "email_notification": "daanvdster@gmail.com"
            }
        ]
        
        print("📝 Adding sample properties...")
        
        for prop in sample_properties:
            # Create dummy analysis result
            dummy_analysis = {
                "analysis": {
                    "market_score": 75.5,
                    "ai_analysis": {
                        "investment_grade": "B+", 
                        "executive_summary": f"Sample analysis for {prop['address']}",
                        "bottom_line": "OVERWEGEN - Sample recommendation"
                    }
                },
                "processing_time_seconds": 5.2
            }
            
            self.add_property(prop, dummy_analysis)
        
        print("✅ Sample data added!")

# Create global instance
sheets_manager = PropertySheetsManager()