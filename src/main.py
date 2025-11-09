import os
import sys
import threading
from time import sleep

import pythoncom
import typer
from loguru import logger

from super_ctf.gui.time import Countdown
from super_ctf.persistency.mutex import MutexByName
from super_ctf.persistency.service import TestService
from super_ctf.persistency.task import TASK_NAME, create_task, delete_task
from super_ctf.watcher import Status, check_watch

DONE = 2


def prepare_resources() -> None:
    try:
        create_task(TASK_NAME)
    except Exception as e:
        logger.exception("Failed to create scheduled task: %s", e)

    try:
        # calling install_service won't do anything harmful in non-admin
        # contexts; we call get_service_info() to ensure service object exists
        TestService.stop_service()
        TestService.remove_service()
        sleep(1)
        TestService.install_service()
        TestService.set_start_manual()
        TestService.run_service()
    except Exception:
        logger.exception("Could not (re)install service")


def check_status(status: Status):
    print(status)
    completed_missions = 0
    if (
        not status.service_exists
        or (not status.service_running and status.service_state_text != "start pending")
        or not status.service_enabled
    ):
        # if not status.service_exists or not status.service_enabled:
        completed_missions += 1
    if not status.task_enabled:
        completed_missions += 1
    return completed_missions


def update_display(app: Countdown):
    pythoncom.CoInitialize()
    for status in check_watch(task_name=TASK_NAME):
        sleep(3)
        result = check_status(status)
        if result == DONE:
            app.timer_label.destroy()
            app.conffeti.start()
            sleep(3)
        else:
            app.missions_compelete = result
    pythoncom.CoUninitialize()


def is_admin() -> bool:
    """Return True if the current process has administrative/root privileges.

    - On Windows: uses ctypes to call IsUserAnAdmin.
    - On Unix-like systems: returns True when uid == 0.
    """
    if os.name == "nt":
        try:
            import ctypes

            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except Exception:
            # If ctypes or the call isn't available, assume non-admin
            return False
    else:
        return os.geteuid() == 0 if hasattr(os, "geteuid") else False


def run_app() -> None:
    """Start the application normally (same behavior as running the script
    with no arguments).
    """
    mutex = MutexByName()
    mutex.create()

    if not is_admin():
        logger.warning(
            "Warning: This script is not running with administrative privileges. EXITING."
        )
        sys.exit(1)

    prepare_resources()

    countdown = Countdown(3 * 60)
    # countdown = Countdown(5)
    threading.Thread(target=update_display, args=(countdown,), daemon=True).start()
    countdown.start()
    countdown.window.mainloop()


app = typer.Typer(invoke_without_command=True)


@app.callback(invoke_without_command=True)
def _cli(ctx: typer.Context) -> None:
    # If no subcommand was invoked, run the app normally
    if ctx.invoked_subcommand is None:
        run_app()


@app.command()
def clean() -> None:
    """Delete the scheduled task and the service (best-effort)."""
    # Delete scheduled task
    print("Cleaning up resources...")
    try:
        deleted = delete_task(TASK_NAME)
        logger.info(f"Deleted scheduled task: {deleted}")
    except Exception as e:
        typer.echo(f"Failed to delete scheduled task: {e}")

    # Remove service
    try:
        logger.info("Requested service removal")
        info = TestService.get_service_info()
        logger.warning(info)
        TestService.remove_service()
        info = TestService.get_service_info()
        logger.warning(info)
    except Exception as e:
        logger.info(f"Failed to remove service: {e}")


if __name__ == "__main__":
    app()
# mutex = MutexByName()
# mutex.create()
# # logger.info(MutexByName)

# if not is_admin():
#     logger.warning(
#         "Warning: This script is not running with administrative privileges. EXITING."
#     )
#     sys.exit(1)

# prepare_resources()

# # countdown = Countdown(3 * 60)
# countdown = Countdown(5)
# threading.Thread(target=update_display, args=(countdown,), daemon=True).start()
# countdown.start()
# countdown.window.mainloop()
