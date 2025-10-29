"""Watcher utilities for checking service and scheduled task health.

Provides a generator `check_watch` that repeatedly checks the TestService
and a scheduled task and yields a status mapping on each iteration.

The generator is cooperative: it yields control back to the caller with the
latest status and then continues after the caller resumes iteration. This
lets callers integrate the watcher into GUI loops or asyncio adapters easily
without imposing its own sleep strategy.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    from collections.abc import Generator

from super_ctf.persistency.service import TestService
from super_ctf.persistency.task import TASK_NAME, check_task_status


class Status(NamedTuple):
    service_exists: bool
    service_running: bool
    service_enabled: bool
    service_state_text: str
    service_start_type: str
    task_enabled: bool


def check_watch(task_name: str = TASK_NAME) -> Generator[Status]:
    """Generator that continuously checks the liveness and configuration of a service
    and a scheduled task.
    This generator polls two sources of truth each iteration:
    - TestService.get_service_info() to obtain current service state and metadata.
    - check_task_status(task_name) to determine whether the scheduled task is
        present and enabled.
    Parameters
    ----------
    task_name : str
            Name of the scheduled task to check. Defaults to the module-level TASK_NAME.
    Yields
    ------
    Status
            An object (or dataclass) containing the following attributes on every
            iteration:
                - service_exists (bool): True if the service is present on the system.
                - service_running (bool): True if the service is currently running.
                - service_enabled (bool): True if the service is configured to start on
                    boot (or enabled according to platform semantics).
                - service_state_text (str): Human-readable state reported by the service
                    provider (e.g. "running", "stopped", "paused").
                - service_start_type (str): Start type description (e.g. "auto", "manual",
                    "disabled") as reported by TestService.
                - task_enabled (bool): True if the named scheduled task appears to be
                    present and enabled.
    Behavior
    --------
    - The generator is infinite; it continues yielding status snapshots until the
        caller stops iteration (for example by breaking a loop or closing a consumer).
    - This generator does not perform any sleeping or timing; the caller controls
        pacing between iterations (suitable for integration in GUI callbacks,
        schedulers, or event loops).
    - No internal exception handling is performed: if TestService.get_service_info()
        or check_task_status() raises an exception, that exception will propagate to
        the caller.
    Notes
    -----
    The exact structure and type name of the yielded object is "Status" as used by
    the surrounding module; callers should inspect or type-hint against that type
    for attribute access.
    """

    while True:
        svc_info = TestService.get_service_info()
        task_ok: bool = check_task_status(task_name)

        yield Status(
            service_exists=bool(svc_info.exists),
            service_running=bool(svc_info.running),
            service_enabled=bool(svc_info.enabled),
            service_state_text=svc_info.state_text,
            service_start_type=svc_info.start_type_text,
            task_enabled=bool(task_ok),
        )


__all__ = ["check_watch"]
