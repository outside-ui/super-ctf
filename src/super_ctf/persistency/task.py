import contextlib
import datetime

from loguru import logger
import win32com.client

# === CONFIGURATION ===
TASK_NAME = "MyPythonScheduledTask"
FILE_TO_RUN = r"C:\Path\To\Your\File.bat"  # or .exe, .py, etc.


def create_task(
    task_name: str = TASK_NAME,
    file_to_run: str = FILE_TO_RUN,
    minutes_from_now: int = 3,
) -> None:
    # Ensure any existing task with this name is removed so we create it from scratch
    with contextlib.suppress(NameError):
        delete_task(task_name)

    # === CALCULATE START TIME (3 minutes from now) ===
    # Use timezone-aware timestamp (system local timezone)
    tz = datetime.datetime.now().astimezone().tzinfo
    if tz is None:
        logger.debug("tzinfo not available! Using UTC as fallback.")
    else:
        tz = datetime.UTC

    start_time = datetime.datetime.now(tz=tz) + datetime.timedelta(
        minutes=minutes_from_now
    )
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
    task_create_or_update = 6
    task_logon_interactive_token = 3

    root_folder.RegisterTaskDefinition(
        task_name,
        task_def,
        task_create_or_update,
        None,  # no username
        None,  # no password
        task_logon_interactive_token,
    )

    logger.debug(f"Task '{task_name}' created successfully.")
    logger.debug(f"⏰ It will run at: {start_time_str}")


def delete_task(task_name: str = TASK_NAME) -> bool:
    """Delete a scheduled task if it exists.

    Returns True if the task was found and deleted, False if it did not exist.
    """
    scheduler = win32com.client.Dispatch("Schedule.Service")
    scheduler.Connect()
    root_folder = scheduler.GetFolder("\\")

    try:
        # Attempt to get the task; if it doesn't exist GetTask will raise
        root_folder.GetTask(task_name)
    except Exception:  # noqa: BLE001
        logger.debug(f"Task '{task_name}' does not exist; nothing to delete.")
        return False

    # If we got here, the task exists; unregister it
    try:
        task_ignore_registration_triggers = 0
        root_folder.DeleteTask(task_name, task_ignore_registration_triggers)
    except Exception as exc:  # noqa: BLE001
        logger.debug(f"Failed to delete task '{task_name}': {exc}")
        return False
    else:
        logger.debug(f"Task '{task_name}' deleted.")
        return True


def check_task_status(task_name: str = TASK_NAME) -> bool:
    scheduler = win32com.client.Dispatch("Schedule.Service")
    scheduler.Connect()
    root_folder = scheduler.GetFolder("\\")

    try:
        task = root_folder.GetTask(task_name)
    except Exception:  # noqa: BLE001
        logger.debug(f"❌ Task '{task_name}' not found.")
        return False

    # Get enabled/disabled status
    enabled = bool(task.Enabled)
    if enabled:
        logger.debug(f"✅ Task '{task_name}' exists and is ENABLED.")
    else:
        logger.debug(f"⚠️ Task '{task_name}' exists but is DISABLED.")
    return enabled


if __name__ == "__main__":
    create_task(TASK_NAME, FILE_TO_RUN)
    check_task_status(TASK_NAME)
    delete_task(TASK_NAME)
    # === Example usage ===
    check_task_status(TASK_NAME)
