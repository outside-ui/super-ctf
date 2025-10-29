import os
import socket
import sys
from dataclasses import dataclass

from loguru import logger
import pywintypes
import servicemanager
import win32api
import win32con
import win32event
import win32service
import win32serviceutil

# Map numeric state to readable text
STATES: dict[int, str] = {
    win32service.SERVICE_STOPPED: "stopped",
    win32service.SERVICE_START_PENDING: "start pending",
    win32service.SERVICE_STOP_PENDING: "stop pending",
    win32service.SERVICE_RUNNING: "running",
    win32service.SERVICE_CONTINUE_PENDING: "continue pending",
    win32service.SERVICE_PAUSE_PENDING: "pause pending",
    win32service.SERVICE_PAUSED: "paused",
}

START_TYPES = {
    win32service.SERVICE_AUTO_START: "auto",
    win32service.SERVICE_DEMAND_START: "manual",
    win32service.SERVICE_DISABLED: "disabled",
}


@dataclass
class ServiceInfo:
    exists: bool
    running: bool
    enabled: bool
    state_text: str
    start_type_text: str


class TestService(win32serviceutil.ServiceFramework):
    _svc_name_ = "CTFService"
    _svc_display_name_ = "CTF Service"
    _svc_description_ = "Good Job"

    def __init__(self, args) -> None:  # noqa: ANN001
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)

    def SvcStop(self) -> None:
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self) -> None:
        rc = None
        while rc != win32event.WAIT_OBJECT_0:
            with open("C:\\TestService03.log", "a") as f:
                f.write("test service 03 is running...\n")
            rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)

    @classmethod
    def install_service(cls, exe_path: str | None = None) -> None:
        """
        Install (register) the Windows service programmatically.
        If exe_path is not given, it uses the current script.
        """

        if exe_path is None:
            exe_path = sys.executable + f' "{os.path.abspath(sys.argv[0])}"'
            print(exe_path)
        try:
            # win32serviceutil.InstallService(
            #     serviceName=cls._svc_name_,
            #     displayName=cls._svc_display_name_,
            #     exeName=exe_path,
            #     description=cls._svc_description_,
            #     startType=win32service.SERVICE_AUTO_START,
            # )
            win32serviceutil.HandleCommandLine(TestService, argv=["NONE", "install"])
            logger.debug(f"✅ Service '{cls._svc_name_}' installed successfully.")
        except pywintypes.error as e:
            logger.debug(f"❌ Failed to install service '{cls._svc_name_}': {e}")

    @classmethod
    def remove_service(cls, exe_path: str | None = None) -> None:
        """
        Install (register) the Windows service programmatically.
        If exe_path is not given, it uses the current script.
        """

        if exe_path is None:
            exe_path = sys.executable + f' "{os.path.abspath(sys.argv[0])}"'

        try:
            win32serviceutil.HandleCommandLine(TestService, argv=["NONE", "remove"])
            logger.debug(f"✅ Service '{cls._svc_name_}' removed successfully.")
        except pywintypes.error as e:
            logger.debug(f"❌ Failed to remove service '{cls._svc_name_}': {e}")

    @classmethod
    def run_service(cls) -> None:
        """
        Start the service programmatically (without command-line use).
        """
        try:
            win32serviceutil.StartService(cls._svc_name_)
            logger.debug(f"🚀 Service '{cls._svc_name_}' started successfully.")
        except pywintypes.error as e:
            logger.debug(f"❌ Failed to start service '{cls._svc_name_}': {e}")

    @classmethod
    def stop_service(cls) -> None:
        """
        Stop the service programmatically (without command-line use).
        """
        try:
            win32serviceutil.StopService(cls._svc_name_)
            logger.debug(f"🚀 Service '{cls._svc_name_}' Stopped successfully.")
        except pywintypes.error as e:
            logger.debug(f"❌ Failed to stop service '{cls._svc_name_}': {e}")

    @classmethod
    def get_service_info(cls) -> ServiceInfo:
        service_name = cls._svc_name_

        try:
            # --- 1️⃣ Query the service status ---
            status = win32serviceutil.QueryServiceStatus(service_name)
            state = status[1]
            is_running = state == win32service.SERVICE_RUNNING

            # --- 2️⃣ Query the startup type (enabled/disabled/manual) ---
            scm = win32service.OpenSCManager(
                None, None, win32service.SC_MANAGER_CONNECT
            )
            service = win32service.OpenService(
                scm,
                service_name,
                win32service.SERVICE_QUERY_CONFIG,
            )
            config = win32service.QueryServiceConfig(service)
            start_type = config[1]  # second element is the start type
            is_enabled = start_type != win32service.SERVICE_DISABLED

            # Cleanup handles
            win32service.CloseServiceHandle(service)
            win32service.CloseServiceHandle(scm)

            logger.debug(f"✅ Service '{service_name}' exists.")
            logger.debug(f"   → State: {STATES.get(state, 'unknown')} ({state})")
            logger.debug(
                f"   → Enabled: {is_enabled} ({START_TYPES.get(start_type, 'unknown')})"
            )

            return ServiceInfo(
                exists=True,
                running=is_running,
                enabled=is_enabled,
                state_text=STATES.get(state, "unknown"),
                start_type_text=START_TYPES.get(start_type, "unknown"),
            )

        except pywintypes.error as e:
            logger.debug(
                f"❌ Service '{service_name}' does not exist or could not be queried: {e}"
            )
            return ServiceInfo(
                exists=False,
                running=False,
                enabled=False,
                state_text="None",
                start_type_text="None",
            )


def show_popup(message: str, title: str = "Notification") -> None:
    # hwnd = 0 (no parent window)
    win32api.MessageBox(0, message, title, win32con.MB_OK)


if __name__ == "__main__":
    # TestService.install_service(r"C:\Users\john\Desktop\git\super-ctf\.venv\pythonservice.exe")
    TestService.get_service_info()
    if servicemanager.RunningAsService():
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(TestService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        # win32serviceutil.HandleCommandLine(TestService)
        show_popup("TEST OUT")
        TestService.install_service()
        TestService.run_service()
        TestService.get_service_info()
