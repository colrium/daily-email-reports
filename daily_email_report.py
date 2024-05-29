import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv
from prompt_toolkit import prompt, PromptSession
from prompt_toolkit.history import FileHistory
from prompt_toolkit.auto_suggest import AutoSuggestFromHistory
from prompt_toolkit.completion import WordCompleter
from radiolist_dialog import radiolist_dialog
import os

tasks = []
# Load environment variables from .env file
load_dotenv()

session = PromptSession(history=FileHistory("~/.prompt-history"))


def add_task():
    prompt_for_tasks(-1)


def list_tasks():
    print("\nTasks:")
    for idx, task in enumerate(tasks):
        print(f"{idx}. {task[0]} (Priority: {task[1]})")


def update_task():
    list_tasks()
    task_idx = int(prompt("Select task number to update: "))
    description = prompt("Enter new description: ")
    priority = prompt("Enter new priority (low/medium/high): ")
    tasks[task_idx] = (description, priority)
    print("Task updated.")


def delete_task():
    list_tasks()
    task_idx = int(prompt("Select task number to delete: "))
    del tasks[task_idx]
    print("Task deleted.")


def task_manager_prompt():
    completer = WordCompleter(["add", "list", "update", "delete", "exit"])
    option = prompt("Task Manager> ", completer=completer)
    return option.strip()


def prompt_for_tasks(index=-1):
    project_name = prompt(
        "Enter the project name: ", auto_suggest=AutoSuggestFromHistory()
    )

    default_task_type = tasks[index].task_type if index >= 0 else "Bug"
    default_ticket_no = tasks[index].ticket_no if index >= 0 else ""
    default_task_name = tasks[index].task_name if index >= 0 else ""
    default_checklist = tasks[index].checklist if index >= 0 else []

    while True:
        task_type = (
            radiolist_dialog(
                title=f"Type  (Enter to proceed. Default: {default_task_type}):",
                values=[
                    ("Bug", "Bug"),
                    ("Task", "Task"),
                    ("Feature", "Feature"),
                    ("Support", "Support"),
                ],
            )
            or default_task_type
        )
        ticket_no = (
            prompt(
                f"Enter the ticket number (Enter ({default_ticket_no})): ",
                auto_suggest=AutoSuggestFromHistory(),
            )
            or default_ticket_no
        )
        if not ticket_no:
            break
        task_name = (
            prompt(f"Enter the task name: {default_task_name}") or default_task_name
        )
        eta = input("Enter the ETA in hours (default: 1): ") or "1"
        checklist = []
        while True:
            checklist_item = input(
                "Enter a checklist item (or press Enter to finish): "
            )
            if not checklist_item:
                break
            status = (
                radiolist_dialog(
                    title="Status:",
                    values=[
                        ("Not Started", "Not Started"),
                        ("WIP", "WIP"),
                        ("On-hold", "On-hold"),
                        ("Done", "Done"),
                    ],
                )
                or "Not Started"
            )
            spent_hours = ""
            if status in ["WIP", "Done"]:
                spent_hours = input("Enter spent hours (default: 0): ") or "0"
                if spent_hours == "0":
                    spent_hours = ""
                else:
                    spent_hours = f"Spent {spent_hours}hrs - "
            checklist.append(f"{spent_hours}{checklist_item} - {status}")

        task = {
            "task_type": task_type,
            "ticket_no": ticket_no,
            "task_name": task_name,
            "eta": eta,
            "checklist": checklist,
        }
        tasks.append(task)

    return project_name, tasks


def format_tasks(project_name, tasks):
    formatted_tasks = f"Tasks WIP\n    {project_name}\n"
    for idx, task in enumerate(tasks, start=1):
        formatted_tasks += f"\n    {idx}. #{task['ticket_no']} {task['task_name']} - ETA {task['eta']}hrs\n"
        for checklist_idx, checklist_item in enumerate(task["checklist"], start=1):
            formatted_tasks += f"        {checklist_idx}. {checklist_item}\n"
    return formatted_tasks


def save_email_body(subject, body):
    # Ensure the directory exists
    if not os.path.exists("emails"):
        os.makedirs("emails")

    # Create a valid filename
    filename = f"emails/{subject.replace(' ', '_').replace(':', '_')}.txt"

    # Save the body to the file
    with open(filename, "w") as file:
        file.write(body)
    print(f"Email body saved to {filename}")


def send_email(subject, body):
    # Email account credentials
    from_email = os.getenv("EMAIL_ADDRESS")
    password = os.getenv("EMAIL_PASSWORD")
    to_email = os.getenv("TO_EMAIL")
    cc_emails = os.getenv("CC_EMAILS").split(",")

    # Create the email
    msg = MIMEMultipart()
    msg["From"] = from_email
    msg["To"] = to_email
    msg["Cc"] = ", ".join(cc_emails)
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    # Get all recipients (to + cc)
    recipients = [to_email] + cc_emails

    # Send the email
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(from_email, password)
        text = msg.as_string()
        server.sendmail(from_email, recipients, text)
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")


def main():
    # Prompt for the day's tasks
    project_name, tasks = prompt_for_tasks()
    formatted_tasks = format_tasks(project_name, tasks)

    while True:
        option = task_manager_prompt()
        if option == "add":
            add_task()
        elif option == "list":
            list_tasks()
        elif option == "update":
            update_task()
        elif option == "delete":
            delete_task()
        elif option == "exit":
            print("Exiting Task Manager.")
            break

    # Capture the current date and format it
    current_date = datetime.now().strftime("%d-%b-%Y")

    # Prompt for the subject with a default value
    default_subject = f"Tasks for {current_date} - Mutugi (WFH)"
    subject = (
        input(f"Enter the email subject (default: '{default_subject}'): ")
        or default_subject
    )

    # Save the email body to a file
    save_email_body(subject, formatted_tasks)

    # Prompt for sending immediately or scheduling
    send_choice = (
        input(
            "Do you want to send the email immediately or schedule it? (immediate/schedule): "
        )
        .strip()
        .lower()
    )
    if send_choice == "immediate":
        send_email(subject, formatted_tasks)
    elif send_choice == "schedule":
        # Prompt for the schedule time
        schedule_time = input(
            "Enter the time to send the email (HH:MM format, 24-hour clock): "
        )
        try:
            # Validate time format
            time.strptime(schedule_time, "%H:%M")
            # Schedule the email
            schedule.every().day.at(schedule_time).do(
                send_email, subject=subject, body=formatted_tasks
            )
            print(f"Email scheduled to be sent at {schedule_time} daily.")
            while True:
                schedule.run_pending()
                time.sleep(1)
        except ValueError:
            print("Invalid time format. Please enter time in HH:MM format.")
    else:
        print("Invalid choice. Please choose either 'immediate' or 'schedule'.")


if __name__ == "__main__":
    main()
