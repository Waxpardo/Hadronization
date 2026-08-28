#!/usr/bin/env python3
"""Reset supervisor-handled signals, then replace this process with a command."""

from __future__ import annotations

import os
import signal
import sys
from pathlib import Path


RESET_SIGNALS = (signal.SIGHUP, signal.SIGINT, signal.SIGTERM)


def main() -> int:
    if len(sys.argv) < 2:
        print(
            "SIGNAL_LAUNCH_REFUSAL invalid invocation: expected COMMAND [ARG ...]",
            file=sys.stderr,
        )
        return 2

    command = sys.argv[1:]
    for handled_signal in RESET_SIGNALS:
        try:
            signal.signal(handled_signal, signal.SIG_DFL)
        except (OSError, ValueError) as error:
            print(
                "SIGNAL_LAUNCH_REFUSAL cannot reset "
                f"{signal.Signals(handled_signal).name}: {error}",
                file=sys.stderr,
            )
            return 125

    try:
        os.execvpe(command[0], command, os.environ)
    except OSError as error:
        print(
            "SIGNAL_LAUNCH_REFUSAL exec failed "
            f"command={Path(command[0]).name}: {error}",
            file=sys.stderr,
        )
        return 127


if __name__ == "__main__":
    raise SystemExit(main())
