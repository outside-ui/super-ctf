import os, sys, threading, pythoncom
from time import sleep
from loguru import logger
from super_ctf.gui.time import Countdown
from super_ctf.persistency.mutex import MutexByName
from super_ctf.persistency.service import TestService
from super_ctf.persistency.task import TASK_NAME, create_task, delete_task
from super_ctf.watcher import Status, check_watch


DONE = 2

def prepare_resources():
    try:
        create_task(TASK_NAME)
    except Exception as e:
        logger.exception("Failed to create scheduled task: %s", e)

    try:
        # calling install_service won't do anything harmful in non-admin
        # contexts; we call get_service_info() to ensure service object exists
        TestService.install_service()
        TestService.run_service()
    except Exception:
        logger.debug("Could not (re)install service; continuing for test")


def check_status(status: Status):
    print(status)
    completed_missions = 0
    if not status.service_exists or not status.service_running or not status.service_enabled:
    # if not status.service_exists or not status.service_enabled:
        completed_missions += 1
    if not status.task_enabled:
        completed_missions += 1
    return completed_missions


def update_display(app: Countdown):
    print("here")
    pythoncom.CoInitialize()
    for status in check_watch(task_name=TASK_NAME):
        print("hereeeeee")
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


if __name__ == "__main__":
    
    mutex = MutexByName()
    mutex.create()
    logger.info(MutexByName)

    if not is_admin():
        logger.warning(
            "Warning: This script is not running with administrative privileges. EXITING."
        )
        sys.exit(1)
    
    prepare_resources()
    
    countdown = Countdown(3 *60)
    threading.Thread(target=update_display, args=(countdown,), daemon=True).start()
    countdown.start()
    countdown.window.mainloop()