import datetime

import win32com.client

# === CONFIGURATION ===
TASK_NAME = "MyPythonScheduledTask"
FILE_TO_RUN = r"C:\Path\To\Your\File.bat"  # or .exe, .py, etc.


def create_task(
    task_name: str = TASK_NAME,
    file_to_run: str = FILE_TO_RUN,
    minutes_from_now: int = 3,
) -> None:
    # === CALCULATE START TIME (3 minutes from now) ===
    start_time = datetime.datetime.now() + datetime.timedelta(minutes=minutes_from_now)
    start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%S")

    # === CREATE THE SCHEDULER OBJECT ===
    scheduler = win32com.client.Dispatch("Schedule.Service")
    scheduler.Connect()

    root_folder = scheduler.GetFolder("\\")

    # === CREATE THE TASK DEFINITION ===
    task_def = scheduler.NewTask(0)

    # Registration info (optional)
    task_def.RegistrationInfo.Description = "Runs a file once, 3 minutes from now."
    task_def.RegistrationInfo.Author = "The Man Script"

    # Task settings
    task_def.Settings.Enabled = True
    task_def.Settings.StartWhenAvailable = True
    task_def.Settings.Hidden = False

    # === CREATE A TRIGGER (Time-based) ===
    trigger = task_def.Triggers.Create(1)  # 1 = TASK_TRIGGER_TIME
    trigger.StartBoundary = start_time_str
    trigger.Enabled = True

    # === CREATE THE ACTION ===
    action = task_def.Actions.Create(0)  # 0 = TASK_ACTION_EXEC
    action.Path = file_to_run

    # === REGISTER THE TASK ===
    TASK_CREATE_OR_UPDATE = 6
    TASK_LOGON_INTERACTIVE_TOKEN = 3

    root_folder.RegisterTaskDefinition(
        task_name,
        task_def,
        TASK_CREATE_OR_UPDATE,
        None,  # no username
        None,  # no password
        TASK_LOGON_INTERACTIVE_TOKEN,
    )

    print(f"✅ Task '{TASK_NAME}' created successfully.")
    print(f"⏰ It will run at: {start_time_str}")


def check_task_status(task_name: str = TASK_NAME) -> bool:
    scheduler = win32com.client.Dispatch("Schedule.Service")
    scheduler.Connect()
    root_folder = scheduler.GetFolder("\\")

    try:
        task = root_folder.GetTask(task_name)
    except Exception:  # noqa: BLE001
        print(f"❌ Task '{task_name}' not found.")
        return False

    # Get enabled/disabled status
    enabled = bool(task.Enabled)
    if enabled:
        print(f"✅ Task '{task_name}' exists and is ENABLED.")
    else:
        print(f"⚠️ Task '{task_name}' exists but is DISABLED.")
    return enabled


if __name__ == "__main__":
    create_task(TASK_NAME, FILE_TO_RUN)
    # === Example usage ===
    check_task_status(TASK_NAME)
