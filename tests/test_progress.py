"""Tests for mempalace.progress.ProgressReporter."""

import io

from mempalace.progress import ProgressReporter


def test_progress_reporter_writes_to_stringio():
    stream = io.StringIO()
    reporter = ProgressReporter(total=3, label="Mining", stream=stream, enabled=True)
    reporter.update(1, "file_a.py")
    reporter.update(2, "file_b.py")
    reporter.update(3, "file_c.py")
    reporter.finish("Done — 3 files")

    output = stream.getvalue()
    assert "Mining:" in output
    assert "file_a.py" in output
    assert "Done — 3 files" in output


def test_progress_reporter_disabled_writes_nothing():
    stream = io.StringIO()
    reporter = ProgressReporter(total=3, label="Mining", stream=stream, enabled=False)
    reporter.update(1, "file_a.py")
    reporter.finish("Done")

    assert stream.getvalue() == ""


def test_progress_reporter_throttles_on_non_tty():
    """On non-TTY streams updates are throttled to ~10% intervals."""
    stream = io.StringIO()
    reporter = ProgressReporter(total=100, label="Mining", stream=stream, enabled=True)
    for i in range(1, 101):
        reporter.update(i)
    reporter.finish("Done")

    lines = [line for line in stream.getvalue().split("\n") if line.strip()]
    # Throttle step is 10, plus finish line => roughly 11 updates, but we
    # allow some slack because the first and last updates are always written.
    assert 8 <= len(lines) <= 15


def test_progress_reporter_always_renders_first_and_last():
    stream = io.StringIO()
    reporter = ProgressReporter(total=1000, label="Mining", stream=stream, enabled=True)
    reporter.update(1)
    reporter.update(1000)
    reporter.finish("Done")

    output = stream.getvalue()
    assert "1/1000" in output
    assert "1000/1000" in output
