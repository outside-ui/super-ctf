import os
import sys
from time import sleep

from loguru import logger

from super_ctf.gui.timer import Countdown
from super_ctf.persistency.mutex import MutexByName
from super_ctf.persistency.service import TestService
from super_ctf.persistency.task import TASK_NAME, create_task, delete_task
from super_ctf.watcher import Status, check_watch


def status_logic(status: Status) -> tuple[int, str]:
    steps = 2
    if (
        not status.service_exists
        or not status.service_running
        or not status.service_enabled
    ):
        steps -= 1
    if not status.task_enabled:
        steps -= 1

    out = ""
    match steps:
        case 2:
            out = "✅ All attack systems operational | You can do it, stop the attack!"
        case 1:
            out = "⚠️ Some attack systems degraded | Stop another system!"
        case 0:
            out = "❌ Critical failure in attack systems detected | Success! You saved the country, you hero."
        case _:
            out = "❓ Unknown status | How did we get here?"

    return steps, out


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

    def test_status_flow():
        """Test routine:

        1) create scheduled task and (attempt to) create/register service
        2) iterate check_watch and print status
        3) on 2nd iteration delete the scheduled task
        4) on 3rd iteration delete the service
        """

        # Prepare resources
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

        for idx, status in enumerate(check_watch(task_name=TASK_NAME)):
            sleep(4)
            steps, message = status_logic(status)
            logger.info(f"iteration={idx + 1} steps={steps} message={message}")

            # On second iteration remove the scheduled task
            if idx == 1:
                try:
                    deleted = delete_task(TASK_NAME)
                    logger.info("Deleted scheduled task: %s", deleted)
                except Exception:
                    logger.exception("Failed to delete scheduled task")

            # On third iteration remove the service (best-effort)
            if idx == 2:
                # There's no explicit service.delete helper; try to stop then
                # print a message — TestService.run_service/start_service is available
                # but removing a registered Windows service programmatically would
                # require win32 APIs; we'll at least attempt to stop it via
                # win32serviceutil if available.
                logger.info("Attempting to stop the service (best-effort)")
                # Best-effort: stop then remove the service using helpers
                try:
                    TestService.stop_service()
                    logger.info("Requested service stop")
                except Exception:
                    logger.debug("Could not stop service; continuing")

            if idx == 3:
                logger.info("Attempting to uninstall the service (best-effort)")
                try:
                    TestService.remove_service()
                    logger.info("Requested service removal")
                except Exception:
                    logger.debug("Could not remove service; continuing")

            if idx >= 4:
                break

    test_status_flow()

    Countdown(10).start()
