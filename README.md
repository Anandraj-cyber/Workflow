# CSV Upload Service

This script reads CSV files from a folder, processes each row and sends the data to an external API, writes a log of the results, and sends an email report when done.

I built this to automate the data upload process for marine engine sensor files.

---

## What it does

1. Looks for CSV files in the `done/new/` folder
2. Cleans the headers (removes first 7 characters if column starts with "S")
3. Sends each row as a POST request to the Vedna API
4. Logs success and failure counts to a daily log file in `logs/`
5. Moves the processed file to `done/success/`
6. Sends an HTML email report with the summary

---

## Project structure

```
project/
├── src/                        <- set this as Data_src environment variable
│   ├── upload.py               <- main script
│   ├── logtemplate.html        <- HTML email template
│   └── done/
│       ├── new/                <- place your CSV files here before running
│       ├── success/            <- files move here after successful processing
│       └── error/              <- files move here if something goes wrong
├── logs/                       <- daily log CSV files are saved here
├── requirements.txt
└── README.md
```

---

## Requirements

Python 3.9 or above. Check with:

```
python --version
```

Download Python from https://www.python.org/downloads/ if not installed.
On Windows make sure to check "Add Python to PATH" during setup.

---

## Packages needed

Only two packages need to be installed. Everything else is from the Python standard library.

```
pandas>=2.0.0
requests>=2.31.0
```

What each one does:
- pandas - reads and processes the CSV files
- requests - sends HTTP POST requests to the API

---

## Imports used in the code

From pip (need to install):
```python
import pandas as pd       # CSV reading and processing
import requests           # HTTP POST to API
```

From Python standard library (no install needed):
```python
import os                 # folder paths and environment variables
import shutil             # moving files between folders
import smtplib            # sending emails
from email.message import EmailMessage    # building email content
from datetime import datetime, timezone   # timestamps
```

---

## How to set up

### Step 1 - Clone or download the project

```
git clone https://github.com/YOUR_USERNAME/csv-upload-service.git
cd csv-upload-service
```

### Step 2 - Create a virtual environment

Windows:
```
python -m venv venv
venv\Scripts\activate
```

Mac/Linux:
```
python3 -m venv venv
source venv/bin/activate
```

You will see (venv) at the start of your terminal once it is active.

In VS Code:
1. Press Ctrl + Shift + P
2. Type Python: Select Interpreter
3. Select the venv option
4. Open a new terminal and it activates automatically

To deactivate:
```
deactivate
```

### Step 3 - Install the packages

```
pip install -r requirements.txt
```

This will download and install pandas and requests.

Verify:
```
pip list
```

You should see pandas and requests in the list.

### Step 4 - Set up environment variables

The script reads config from environment variables. You need to set these before running.

Windows (Command Prompt):
```
set Data_src=C:\path\to\your\src\folder
set MAIL_USER=your_email@domain.com
set MAIL_PASS=your_email_password
```

Windows (PowerShell):
```
$env:Data_src = "C:\path\to\your\src\folder"
$env:MAIL_USER = "your_email@domain.com"
$env:MAIL_PASS = "your_email_password"
```

Mac/Linux:
```
export Data_src=/path/to/your/src/folder
export MAIL_USER=your_email@domain.com
export MAIL_PASS=your_email_password
```

What each variable means:

| Variable | Description | Default if not set |
|----------|-------------|-------------------|
| Data_src | path to the src folder where upload.py is | current working directory |
| MAIL_USER | email address used to send the report | hello@vyasaka.in |
| MAIL_PASS | password for that email account | - |

### Step 5 - Add your CSV files

Place the CSV files you want to upload inside:

```
src/done/new/
```

The script only processes files ending in .csv

### Step 6 - Check the email template

Make sure logtemplate.html is in the same folder as upload.py (inside src/).

The template uses these placeholders which get replaced automatically:
- {{file}} - the filename
- {{total}} - total rows processed
- {{success}} - how many rows were sent successfully
- {{failed}} - how many rows failed
- {{start}} - start time
- {{end}} - end time

---

## How to run

Make sure your virtual environment is active and environment variables are set, then:

```
python upload.py
```

Or if you are inside the src folder:

```
cd src
python upload.py
```

---

## Expected output when running

```
Upload Service Started
Processing: BELKO20260214.csv
MAIL SENT
BELKO20260214.csv moved to SUCCESS folder
Upload Service Finished
```

If no files are found:
```
Upload Service Started
No files found.
Upload Service Finished
```

---

## What happens after it runs

- Processed CSV file moves to `done/success/`
- A log file is created or updated at `logs/upload_log_YYYY-MM-DD.csv`
- An HTML email is sent to the recipient with the summary

Log file columns:
- file_name
- total_records
- success_count
- fail_count
- start_time
- end_time

---

## API details

The script posts each row to this endpoint:

```
POST https://apin.vedna.in/seaguard/api/device/device/{vid}
```

Each row is sent as a JSON payload. The DateAndTime field is combined with the Time field and converted to ISO 8601 format before sending.

If the API returns 200 or 201 it counts as success. Anything else counts as a failure.

---

## Email setup

The script uses SMTP SSL on port 465 to send emails through mail.vyasaka.in

If you are using a different email provider, update these lines in upload.py:

```python
server = smtplib.SMTP_SSL("mail.vyasaka.in", 465, timeout=10)
```

Replace "mail.vyasaka.in" with your SMTP host and 465 with your port.

---

## Common issues

**ModuleNotFoundError for pandas or requests** - run pip install -r requirements.txt

**No files found** - make sure CSV files are placed inside done/new/ not the root folder

**Email failed** - check MAIL_USER and MAIL_PASS environment variables, also check if your email provider allows SMTP access

**API returning errors** - check your internet connection, the vid in the API URL might need to be updated

**File not moving to success** - check folder permissions, make sure done/success/ folder exists (it is created automatically but worth checking)

**datetime parse error** - make sure the DateAndTime and Time columns exist in your CSV with the correct names
