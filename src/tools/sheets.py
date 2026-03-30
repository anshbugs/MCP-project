import os
from google.oauth2.service_account import Credentials
import gspread

SPREADSHEET_ID = "1R6rWWw0iem-xUM3tDKCT7ohlXQv549D8iGwvcBaWsIc"
CREDENTIALS_FILE = "google_credentials.json"

def append_to_sheet(row_data: list):
    """
    Appends a row of data to the Google Sheet.
    Silently fails and returns False if the config file hasn't been set up by the user yet.
    """
    if not os.path.exists(CREDENTIALS_FILE):
        print(f"[Sheets Integration] Skipped: '{CREDENTIALS_FILE}' not found in the root directory.")
        return False
        
    try:
        scopes = [
            "https://www.googleapis.com/auth/spreadsheets",
            "https://www.googleapis.com/auth/drive"
        ]
        credentials = Credentials.from_service_account_file(CREDENTIALS_FILE, scopes=scopes)
        client = gspread.authorize(credentials)
        
        # Open by ID and select the first worksheet
        sheet = client.open_by_key(SPREADSHEET_ID).sheet1
        sheet.append_row(row_data)
        
        print(f"[Sheets Integration] Successfully appended {row_data[1]} to Google Sheets.")
        return True
    except Exception as e:
        print(f"[Sheets Integration] Failed to write to Google Sheets: {str(e)}")
        return False
