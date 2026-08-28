#!/usr/bin/env python3
"""Launch one command as a new session leader after a parent handshake."""

from __future__ import annotations

import os
import sys
import time
from pathlib import Path


def main() -> int:
    if len(sys.argv) < 5:
        print(
            "usage: launch_in_new_session.py READY_FILE GO_FILE PARENT_PID "
            "COMMAND [ARG ...]",
            file=sys.stderr,
        )
        return 2
    ready_file = Path(sys.argv[1])
    go_file = Path(sys.argv[2])
    try:
        parent_pid = int(sys.argv[3])
    except ValueError:
        print("session launcher: PARENT_PID is not an integer", file=sys.stderr)
        return 2
    command = sys.argv[4:]
    os.setsid()
    pid = os.getpid()
    pgid = os.getpgrp()
    sid = os.getsid(0)
    if pid != pgid or pid != sid:
        print(
            f"session launcher: isolation failed pid={pid} pgid={pgid} sid={sid}",
            file=sys.stderr,
        )
        return 125
    descriptor = os.open(
        ready_file,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL,
        0o600,
    )
    try:
        os.write(descriptor, f"{pid} {pgid} {sid}\n".encode("ascii"))
        os.fsync(descriptor)
    finally:
        os.close(descriptor)
    while not go_file.is_file():
        if os.getppid() != parent_pid:
            return 125
        time.sleep(0.01)
    ready_file.unlink(missing_ok=True)
    go_file.unlink(missing_ok=True)
    try:
        os.execvpe(command[0], command, os.environ)
    except OSError as error:
        print(
            f"session launcher: cannot execute {Path(command[0]).name}: {error}",
            file=sys.stderr,
        )
        return 127


if __name__ == "__main__":
    raise SystemExit(main())
