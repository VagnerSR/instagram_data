import requests
import json
import gspread
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os

load_dotenv()


ig_business_account_id = os.getenv("INSTAGRAM_ID")
access_token = os.getenv("ACCESS_TOKEN")

url = f"https://graph.facebook.com/v21.0/{ig_business_account_id}/insights"
params = {
    "metric": "comments,reach",
    "period": "day",
    "since": "2025-03-16",
    "until": "2025-04-10",
    "metric_type": "total_value",
    "breakdown": "media_product_type",
    "access_token": access_token
}

response = requests.get(url, params=params)
data = response.json()

print("Instagram insights:")
print(json.dumps(data, indent=2))

SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive'
]

SERVICE_ACCOUNT_FILE = 'credentials.json'

creds = Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
client = gspread.authorize(creds)

spreadsheet_name = os.getenv("SHEET_NAME")
spreadsheet = client.open(spreadsheet_name)
worksheet = spreadsheet.sheet1

rows = []
rows.append(["Métrica", "Período", "Valores"])

if "data" in data:
    for item in data["data"]:
        name = item.get("name", "N/A")
        period = item.get("period", "N/A")
        values_str = json.dumps(item.get("values", []))
        rows.append([name, period, values_str])
else:
    rows.append(["Nenhum dado", "", ""])

worksheet.clear()

worksheet.update(values=rows, range_name="A1")

print("Dados enviados com sucesso para o Google Sheets!")
