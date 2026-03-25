from __future__ import annotations

import os
import sys
import time
from dataclasses import dataclass

if os.name != "nt":
    import select
    import termios
    import tty
else:
    import msvcrt


@dataclass(frozen=True)
class TimedInputResult:
    answer: str
    time_taken: float
    timed_out: bool


class CountdownDisplay:
    """Small helper for rendering a one-line countdown in the CLI."""

    def __init__(self, label: str, total_seconds: int) -> None:
        self.label = label
        self.total_seconds = max(1, total_seconds)

    def render(self, seconds_left: int, suffix: str = "") -> None:
        message = f"\r{self.label}: {seconds_left:02d}s left"
        if suffix:
            message += f" | {suffix}"
        sys.stdout.write(message)
        sys.stdout.flush()

    def clear(self) -> None:
        sys.stdout.write("\r" + (" " * 120) + "\r")
        sys.stdout.flush()


def _timed_input_windows(prompt: str, time_limit: int) -> TimedInputResult:
    display = CountdownDisplay("Time remaining", time_limit)
    buffer: list[str] = []
    start = time.monotonic()

    print(prompt)
    while True:
        elapsed = time.monotonic() - start
        remaining = max(0, time_limit - int(elapsed))
        display.render(remaining, f"Your answer: {''.join(buffer)}")

        if elapsed >= time_limit:
            display.clear()
            print("Time is up.")
            return TimedInputResult(answer="".join(buffer).strip(), time_taken=float(time_limit), timed_out=True)

        if msvcrt.kbhit():
            char = msvcrt.getwche()
            if char in ("\r", "\n"):
                display.clear()
                print()
                return TimedInputResult(
                    answer="".join(buffer).strip(),
                    time_taken=min(time.monotonic() - start, float(time_limit)),
                    timed_out=False,
                )
            if char == "\003":
                raise KeyboardInterrupt
            if char in ("\b", "\x7f"):
                if buffer:
                    buffer.pop()
                continue
            if char.isprintable():
                buffer.append(char)

        time.sleep(0.1)


def _timed_input_posix(prompt: str, time_limit: int) -> TimedInputResult:
    display = CountdownDisplay("Time remaining", time_limit)
    buffer: list[str] = []
    start = time.monotonic()
    file_descriptor = sys.stdin.fileno()
    old_settings = termios.tcgetattr(file_descriptor)

    print(prompt)
    try:
        tty.setcbreak(file_descriptor)
        while True:
            elapsed = time.monotonic() - start
            remaining = max(0, time_limit - int(elapsed))
            display.render(remaining, f"Your answer: {''.join(buffer)}")

            if elapsed >= time_limit:
                display.clear()
                print("Time is up.")
                return TimedInputResult(
                    answer="".join(buffer).strip(),
                    time_taken=float(time_limit),
                    timed_out=True,
                )

            ready, _, _ = select.select([sys.stdin], [], [], 0.1)
            if not ready:
                continue

            char = sys.stdin.read(1)
            if char in ("\n", "\r"):
                display.clear()
                print()
                return TimedInputResult(
                    answer="".join(buffer).strip(),
                    time_taken=min(time.monotonic() - start, float(time_limit)),
                    timed_out=False,
                )
            if char == "\x03":
                raise KeyboardInterrupt
            if char in ("\x08", "\x7f"):
                if buffer:
                    buffer.pop()
                continue
            if char.isprintable():
                buffer.append(char)
    finally:
        termios.tcsetattr(file_descriptor, termios.TCSADRAIN, old_settings)


def timed_text_input(prompt: str = "Your answer:", time_limit: int = 60) -> TimedInputResult:
    """Collect CLI input with a visible countdown and a hard time limit."""
    if not sys.stdin.isatty():
        print(prompt)
        start = time.monotonic()
        answer = sys.stdin.readline().strip()
        return TimedInputResult(
            answer=answer,
            time_taken=min(time.monotonic() - start, float(time_limit)),
            timed_out=False,
        )

    if os.name == "nt":
        return _timed_input_windows(prompt=prompt, time_limit=time_limit)
    return _timed_input_posix(prompt=prompt, time_limit=time_limit)
