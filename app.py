from flask import Flask, request
from flask_cors import CORS
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
from pytz import timezone
from linebot import LineBotApi
from linebot.models import TextSendMessage
import requests
from dotenv import load_dotenv
import os

load_dotenv()


app = Flask(__name__)
CORS(app)

scheduler = BackgroundScheduler(timezone="Asia/Tokyo")
scheduler.start()


def send_line_message(message, access_token):
    url = "https://notify-api.line.me/api/notify"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    payload = {"message": message}
    response = requests.post(url, headers=headers, data=payload)
    return response.status_code


access_token = os.getenv("API_KEY")


@app.route("/set_reminder", methods=["POST"])
def set_reminder():
    time = request.json["time"]
    hour, minute = map(int, time.split(":"))
    target_time = datetime.now().replace(
        hour=hour, minute=minute, second=0, microsecond=0
    ) - timedelta(hours=1)
    scheduler.add_job(
        send_line_message,
        "date",
        run_date=target_time,
        args=[f"{time}からMTGがあります", access_token],
    )
    return {"message": "Reminder set successfully"}, 200


if __name__ == "__main__":
    app.run(debug=True)
