"""Simple terminal progress reporter for long-running MemPalace operations."""

import sys
import time


class ProgressReporter:
    """A lightweight progress bar that works on TTYs and in tests.

    On a TTY it overwrites the same line with a ``\r``. On a non-TTY stream it
    prints a line only at 10% intervals to avoid flooding redirected logs. Set
    ``force=True`` to render every update regardless of TTY (useful for
    ``io.StringIO`` test captures).
    """

    def __init__(
        self,
        total: int,
        label: str = "Processing",
        stream=None,
        enabled: bool = True,
    ):
        self.total = max(total, 1)
        self.current = 0
        self.label = label
        self.stream = stream or sys.stderr
        self.tty = self._is_tty()
        self.enabled = enabled
        self.start = time.time()
        self._last_line_len = 0
        self._throttle = max(1, self.total // 10)

    def _is_tty(self) -> bool:
        try:
            return self.stream.isatty()
        except Exception:
            return False

    def _format(self, current: int, message: str = "") -> str:
        pct = min(100, int(100 * current / self.total))
        bar_width = 30
        filled = int(bar_width * current / self.total)
        bar = "█" * filled + "░" * (bar_width - filled)
        elapsed = time.time() - self.start
        eta = ""
        if current > 0 and current < self.total:
            rate = current / elapsed
            remaining = (self.total - current) / rate if rate > 0 else 0
            eta = f" ETA {int(remaining)}s"
        message = message or ""
        return f"{self.label}: [{bar}] {current}/{self.total} ({pct}%) {message}{eta}"

    def update(self, current: int, message: str = ""):
        if not self.enabled or current < 0:
            return
        self.current = current
        if not self.tty and current not in (1, self.total) and current % self._throttle != 0:
            return

        line = self._format(current, message)
        if self.tty:
            self.stream.write(f"\r  {line}")
            self.stream.write(" " * max(0, self._last_line_len - len(line)))
            self.stream.write("\r")
        else:
            self.stream.write(f"  {line}\n")
        self.stream.flush()
        self._last_line_len = len(line) + 2

    def finish(self, message: str = "Done"):
        if not self.enabled:
            return
        if self.tty:
            self.stream.write("\r" + " " * self._last_line_len + "\r")
        self.stream.write(f"  {self.label}: {message}\n")
        self.stream.flush()
