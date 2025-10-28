from dataclasses import dataclass

import win32api
import win32event
import winerror

MUTEX_NAME = "Global\\MyUniqueAppMutex"


@dataclass
class CoolMutex:
    name: str
    h_mutex: None | int = None

    def create(self) -> bool:
        """Return True if created, else the Mutex already exists."""
        # Try to create a named mutex
        self.h_mutex = win32event.CreateMutex(None, False, self.name)  # pyright: ignore[reportArgumentType]  # noqa: FBT003

        # Check if it already exists
        self.last_error = win32api.GetLastError()

        if self.last_error == winerror.ERROR_ALREADY_EXISTS:
            print("Another instance of the Mutex is already up.")
            return False
        print("Creating Mutex normally.")
        return True

    def is_up(self) -> bool:
        self.h_mutex = win32event.CreateMutex(None, False, self.name)  # pyright: ignore[reportArgumentType]  # noqa: FBT003
        last_error = win32api.GetLastError()
        return last_error == winerror.ERROR_ALREADY_EXISTS

    def close(self) -> None:
        # Always release the mutex handle
        if self.h_mutex is not None:
            win32api.CloseHandle(self.h_mutex)
        else:
            print("No hMutex to close.")


if __name__ == "__main__":
    cool = CoolMutex(name=MUTEX_NAME)
    cool.create()
    print(f"{cool.is_up()=}")
    cool.close()
    print(f"{cool.is_up()=}")
