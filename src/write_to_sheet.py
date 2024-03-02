from googleapiclient.discovery import build

def insert_data_to_sheet(google_creds, sheet_id, chosen_date, data):
    service = build('sheets', 'v4', credentials=google_creds)

    # Define the range to insert the data
    range_name = 'A2'  # This specifies starting at column A, row 2

    # Insert the daily data
    body = {'values': [data]}
    result = service.spreadsheets().values().append(
        spreadsheetId=sheet_id, range=range_name,
        valueInputOption='USER_ENTERED', insertDataOption='INSERT_ROWS', body=body).execute()

    print(f"{result.get('updates').get('updatedRows')} rows appended.")

