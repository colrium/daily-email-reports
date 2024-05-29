# Daily Email Report Automation

This script automates the sending of daily email reports, allowing you to include tasks and customize the email subject with the current date.

## Requirements

- Python 3.x
- Required Python libraries: `smtplib`, `email.mime`, `schedule`, `dotenv`

## Installation

1. Clone the repository or download the script
```bash
git clone https://github.com/colrium/daily-email-reports.git
cd daily-email-report
```

2. Create and activate a virtual environment (optional but recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows use `venv\Scripts\activate`
```

3. Install the required Python libraries:
```bash
pip install -r ./requirements.txt
```

## Setup

1. Create a `.env` file in the project directory and add your email credentials and recipients:
```env
EMAIL_ADDRESS=your_email@example.com
EMAIL_PASSWORD=your_password
TO_EMAIL=recipient@example.com
CC_EMAILS=cc1@example.com,cc2@example.com
```

2. **Replace the placeholders in the `.env` file with your actual email details.**

## Usage

1. Run the script:

```bash
python daily_email_report.py
```

2. When prompted, enter the tasks for the day and customize the email subject if desired:

```
Enter today's tasks: [Your tasks here]
Enter the email subject (default: 'Tasks for DD-MMM-YYYY - Mutugi (WFH)'): [Press Enter to use the default subject]
```

3. The script will send an email with the specified tasks and subject at the scheduled time (09:00 daily by default).

## Scheduler

The script uses the `schedule` library to run the `send_email` function daily at 09:00 AM. You can change the scheduled time by modifying the line:

```python
schedule.every().day.at("09:00").do(send_email)
```