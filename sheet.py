import requests
import datetime
import time
import gspread
from google.oauth2.service_account import Credentials
import time
from response_types import InsightsResponse, SimpleInsightsResponse, FollowsAndUnfollowsResponse
from dotenv import load_dotenv
import os

load_dotenv()

start_date = datetime.date(2025, 2, 18)
end_date = datetime.date(2025, 4, 12)
interval_days = 1

scopes = ["https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"]
credentials = Credentials.from_service_account_file("credentials.json", scopes=scopes)
client = gspread.authorize(credentials)
sheet_name = os.getenv("SHEET_NAME")
sheet = client.open(sheet_name).worksheet("Sheet1")

spreadsheet_headers = [
    "Date",
    "Follows",
    "Unfollows",
    "Profile Views",
    "Accounts Engaged",
    "Reach - Post",
    "Reach - Stories",
    "Reach - Carousel Container",
    "Reach - Reels",
    "Reach - Sum",
    "Comments - Post",
    "Comments - Stories",
    "Comments - Carousel Container",
    "Comments - Reels",
    "Comments - Sum",
    "Likes - Post",
    "Likes - Stories",
    "Likes - Carousel Container",
    "Likes - Reels",
    "Likes - Sum",
    "Views - Post",
    "Views - Stories",
    "Views - Carousel Container",
    "Views - Reels",
    "Views - Sum",
]

sheet.clear()
sheet.append_row(spreadsheet_headers)

access_token = os.getenv("ACCESS_TOKEN")
account_id = os.getenv("INSTAGRAM_ID")

def fetch_insights(params):
    url = f"https://graph.facebook.com/v19.0/{account_id}/insights"
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}", response.json())
        return {}

date = start_date
while date < end_date:
    since = int(time.mktime(date.timetuple()))
    until = int(time.mktime((date + datetime.timedelta(days=interval_days)).timetuple()))
    
    row = [str(date)]

    follows_data: FollowsAndUnfollowsResponse = fetch_insights({
        "metric": "follows_and_unfollows",
        "period": "day",
        "metric_type": "total_value",
        "breakdown": "follow_type",
        "since": since,
        "until": until,
        "access_token": access_token
    })
    follows = 0
    unfollows = 0

    for item in follows_data.get("data", []):
        breakdowns = item.get("total_value", {}).get("breakdowns", [])
        for breakdown in breakdowns:
            results = breakdown.get("results", [])
            for result in results:
                dimension = result.get("dimension_values", [None])[0]
                value = result.get("value", 0)
                if dimension == "FOLLOWER":
                    follows += int(value)
                elif dimension == "NON_FOLLOWER":
                    unfollows += int(value)

    row.extend([follows, unfollows])

    time.sleep(2)
    
    engagement_data: SimpleInsightsResponse = fetch_insights({
        "metric": "accounts_engaged,profile_views",
        "period": "day",
        "metric_type": "total_value",
        "since": since,
        "until": until,
        "access_token": access_token
    })
    profile_views = 0
    accounts_engaged = 0

    for item in engagement_data.get("data", []):
        value = item.get("total_value", {}).get("value", 0)
        if item["name"] == "accounts_engaged":
            accounts_engaged += int(value)
        elif item["name"] == "profile_views":
            profile_views += int(value)

    row.extend([profile_views, accounts_engaged])

    time.sleep(2)
    content_data: InsightsResponse = fetch_insights({
        "metric": "reach,comments,likes,views",
        "period": "day",
        "metric_type": "total_value",
        "breakdown": "media_product_type",
        "since": since,
        "until": until,
        "access_token": access_token
    })
    metrics = {
        "reach": {"carousel_container": 0, "story": 0, "post": 0, "reel": 0},
        "comments": {"carousel_container": 0, "story": 0, "post": 0, "reel": 0},
        "likes": {"carousel_container": 0, "story": 0, "post": 0, "reel": 0},
        "views": {"carousel_container": 0, "story": 0, "post": 0, "reel": 0}
    }

    for item in content_data.get("data", []):
        metric_name = item.get("name")
        breakdowns = item.get("total_value", {}).get("breakdowns", [])
        for breakdown in breakdowns:
            for result in breakdown.get("results", []):
                dimension_values = result.get("dimension_values", [])
                if dimension_values:
                    media_type = dimension_values[0].lower() 
                    media_type = media_type.replace("carousel_container", "carousel_container")
                    val = int(result.get("value", 0))
                    if metric_name in metrics and media_type in metrics[metric_name]:
                        metrics[metric_name][media_type] += val

    reach_sum = sum(metrics["reach"].values())
    comments_sum = sum(metrics["comments"].values())
    likes_sum = sum(metrics["likes"].values())
    views_sum = sum(metrics["views"].values())

    row.extend([
        metrics["reach"]["post"],
        metrics["reach"]["story"],
        metrics["reach"]["carousel_container"],
        metrics["reach"]["reel"],
        reach_sum,
        metrics["comments"]["post"],
        metrics["comments"]["story"],
        metrics["comments"]["carousel_container"],
        metrics["comments"]["reel"],
        comments_sum,
        metrics["likes"]["post"],
        metrics["likes"]["story"],
        metrics["likes"]["carousel_container"],
        metrics["likes"]["reel"],
        likes_sum,
        metrics["views"]["post"],
        metrics["views"]["story"],
        metrics["views"]["carousel_container"],
        metrics["views"]["reel"],
        views_sum
    ])

    sheet.append_row(row)

    date += datetime.timedelta(days=interval_days)

print("All set!")