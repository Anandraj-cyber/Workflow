import os
import shutil
import requests
import pandas as pd
import smtplib
from email.message import EmailMessage
from datetime import datetime, timezone

# path setup

BASE_DIR = os.getenv("Data_src") or os.getcwd()
PROJECT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))

DONE_FOLDER = os.path.join(PROJECT_DIR, "done")
SUCCESS_FOLDER = os.path.join(DONE_FOLDER, "success")
ERROR_FOLDER = os.path.join(DONE_FOLDER, "error")
NEW_FOLDER = os.path.join(DONE_FOLDER, "new")
LOG_FOLDER = os.path.join(PROJECT_DIR, "logs")

os.makedirs(SUCCESS_FOLDER, exist_ok=True)
os.makedirs(ERROR_FOLDER, exist_ok=True)
os.makedirs(NEW_FOLDER, exist_ok=True)
os.makedirs(LOG_FOLDER, exist_ok=True)

# email config

EMAIL = os.getenv("MAIL_USER", "hello@vyasaka.in")
PASSWORD = os.getenv("MAIL_PASS", "eropagniS*123")
RECIPIENT_EMAIL = "anandrajvishwanathan@gmail.com"

# csv processing

def process_csv(file_path):

    start_time = datetime.now()

    df = pd.read_csv(file_path, dtype=str)

    # Remove first 7 letters ONLY if header starts with 'S'
    df.columns = [
        col[7:] if col.startswith("S") and len(col) > 7 else col
        for col in df.columns
    ]

    # Save updated headers
    df.to_csv(file_path, index=False)

    df = df.replace(["NA", "nan", ""], None)

    total_records = len(df)
    success_count = 0
    fail_count = 0

    vid = "v-457b3559-9f35-41a9-af53-7a8b24a83e9f"
    API_URL = f"https://apin.vedna.in/seaguard/api/device/device/{vid}"

    headers = {"Content-Type": "application/json"}

    for _, row in df.iterrows():
        try:

            datetime_string = f"{row.get('DateAndTime')} {row.get('Time')}"

            combined_datetime = pd.to_datetime(
                datetime_string,
                errors="coerce",
                utc=True
            )

            if pd.isna(combined_datetime):
                combined_datetime = datetime.utcnow().replace(tzinfo=timezone.utc)

            payload = {
                k: str(v)
                for k, v in row.items()
                if pd.notna(v)
            }

            payload["DateAndTime"] = (
                combined_datetime.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
            )

            response = requests.post(API_URL, json=payload, headers=headers)

            if response.status_code in [200, 201]:
                success_count += 1
            else:
                fail_count += 1

        except Exception as e:
            print("Row failed:", e)
            fail_count += 1

    end_time = datetime.now()

    return {
        "total": total_records,
        "success": success_count,
        "fail": fail_count,
        "start_time": start_time.strftime("%d-%b-%Y %I:%M:%S %p"),
        "end_time": end_time.strftime("%d-%b-%Y %I:%M:%S %p")
    }


# log writer

def write_log(file_name, log_data):

    log_file_name = f"upload_log_{datetime.now().date()}.csv"
    log_file_path = os.path.join(LOG_FOLDER, log_file_name)

    df_log = pd.DataFrame([{
        "file_name": file_name,
        "total_records": log_data["total"],
        "success_count": log_data["success"],
        "fail_count": log_data["fail"],
        "start_time": log_data["start_time"],
        "end_time": log_data["end_time"]
    }])

    if os.path.exists(log_file_path):
        df_log.to_csv(log_file_path, mode='a', header=False, index=False)
    else:
        df_log.to_csv(log_file_path, index=False)


# email sender

def send_email(file_name, log_data):

    try:

        template_path = os.path.join(BASE_DIR, "logtemplate.html")

        with open(template_path, "r") as f:
            html_template = f.read()

        html_content = html_template \
            .replace("{{file}}", file_name) \
            .replace("{{total}}", str(log_data["total"])) \
            .replace("{{success}}", str(log_data["success"])) \
            .replace("{{failed}}", str(log_data["fail"])) \
            .replace("{{start}}", log_data["start_time"]) \
            .replace("{{end}}", log_data["end_time"])

        server = smtplib.SMTP_SSL("mail.vyasaka.in", 465, timeout=10)
        server.login(EMAIL, PASSWORD)

        msg = EmailMessage()
        msg["Subject"] = f"Upload Report - {file_name}"
        msg["From"] = EMAIL
        msg["To"] = RECIPIENT_EMAIL

        msg.set_content("Your email client does not support HTML.")
        msg.add_alternative(html_content, subtype="html")

        server.send_message(msg)
        server.quit()

        print("MAIL SENT")

    except Exception as e:
        print("Email failed:", e)


# file processor

def process_files():

    files = os.listdir(NEW_FOLDER)

    if not files:
        print("No files found.")
        return

    for file in files:

        if file.endswith(".csv"):

            file_path = os.path.join(NEW_FOLDER, file)

            print("Processing:", file)

            log_data = process_csv(file_path)

            write_log(file, log_data)

            shutil.move(file_path, os.path.join(SUCCESS_FOLDER, file))

            print(file, "moved to SUCCESS folder")

            send_email(file, log_data)


# main

if __name__ == "__main__":

    print("Upload Service Started")

    process_files()

    print("Upload Service Finished")
