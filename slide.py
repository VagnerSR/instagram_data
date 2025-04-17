import gspread
from google.oauth2.service_account import Credentials
import matplotlib.pyplot as plt
from googleapiclient.discovery import build
import io
from googleapiclient.http import MediaIoBaseUpload
from dotenv import load_dotenv
import os

load_dotenv()

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets.readonly",
    "https://www.googleapis.com/auth/drive",
    "https://www.googleapis.com/auth/presentations"
]
credentials = Credentials.from_service_account_file("credentials.json", scopes=SCOPES)

gc = gspread.authorize(credentials)
sheet_name = os.getenv("SHEET_NAME")
sheet = gc.open(sheet_name).sheet1
data = sheet.get_all_values()

metrics = [row[0] for row in data[1:]]
dates = data[0][1:]
values = [list(map(lambda x: int(x) if x.isdigit() else 0, row[1:])) for row in data[1:]]

plt.figure(figsize=(12, 6))
for i, metric_data in enumerate(values):
    plt.plot(dates, metric_data, label=metrics[i])

plt.xticks(rotation=45)
plt.xlabel("Dates")
plt.ylabel("Values")
plt.title("Instagram Metrics")
plt.legend()
plt.tight_layout()

chart_path = "instagram_chart.png"
plt.savefig(chart_path)
plt.close()

slides_service = build("slides", "v1", credentials=credentials)
drive_service = build("drive", "v3", credentials=credentials)

presentation_id = os.getenv("PRESENTATION_ID")
presentation = slides_service.presentations().get(presentationId=presentation_id).execute()


file_metadata = {
    "name": "instagram_chart.png",
    "mimeType": "image/png"
}
media = MediaIoBaseUpload(io.FileIO(chart_path, "rb"), mimetype="image/png")
uploaded_file = drive_service.files().create(body=file_metadata, media_body=media, fields="id").execute()
image_file_id = uploaded_file["id"]

drive_service.permissions().create(fileId=image_file_id, body={"role": "reader", "type": "anyone"}).execute()
image_url = f"https://drive.google.com/uc?id={image_file_id}"

slides_service.presentations().batchUpdate(
    presentationId=presentation_id,
    body={
        "requests": [
            {"createSlide": {"slideLayoutReference": {"predefinedLayout": "BLANK"}}},
            {"createImage": {
                "url": image_url,
                "elementProperties": {
                    "pageObjectId": presentation["slides"][1]["objectId"],
                    "size": {
                       "height": {
                        "magnitude": 276.09,
                        "unit": "PT"
                    },
                    "width": {
                        "magnitude": 551.64,
                        "unit": "PT"
                    }
                    },
                    "transform": {
                        "scaleX": 1,
                        "scaleY": 1,
                        "translateX": 34.02,
                        "translateY": 96.38,
                        "unit": "PT"
                    }
                }
            }}
        ]
    }
).execute()

print(f"Presentation created: https://docs.google.com/presentation/d/{presentation_id}/edit")
