from dataclasses import dataclass

import win32api
import win32event
import winerror
from loguru import logger

MUTEX_NAME = "Global\\MyUniqueAppMutex"


@dataclass
class MutexByName:
    name: str = MUTEX_NAME
    h_mutex: None | int = None

    def create(self) -> bool:
        """Return True if created, else the Mutex already exists."""
        # Try to create a named mutex
        self.h_mutex = win32event.CreateMutex(None, False, self.name)  # pyright: ignore[reportArgumentType]
        logger.debug(f"{self.h_mutex=}")
        # Check if it already exists
        self.last_error = win32api.GetLastError()

        if self.last_error == winerror.ERROR_ALREADY_EXISTS:
            logger.debug("Another instance of the Mutex is already up.")
            return False
        logger.debug("Creating Mutex normally.")
        return True

    def is_up(self) -> bool:
        self.h_mutex = win32event.CreateMutex(None, False, self.name)  # pyright: ignore[reportArgumentType]
        last_error = win32api.GetLastError()
        return last_error == winerror.ERROR_ALREADY_EXISTS

    def close(self) -> None:
        # Always release the mutex handle
        if self.h_mutex is not None:
            win32api.CloseHandle(self.h_mutex)
        else:
            logger.debug("No hMutex to close.")


if __name__ == "__main__":
    cool = MutexByName(name=MUTEX_NAME)
    cool.create()
    cool.create()
    logger.info(f"{cool.is_up()=}")
    # cool.close()
    logger.info(f"{cool.is_up()=}")
    input("enter to exit")
