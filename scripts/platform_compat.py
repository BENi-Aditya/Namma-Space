"""Cross-platform compatibility utilities for Windows, macOS, and Linux."""
import contextlib
import os
from pathlib import Path
import signal
import subprocess
import sys

IS_WINDOWS = sys.platform == "win32"


@contextlib.contextmanager
def file_lock(file_obj, exclusive=True, non_blocking=False):
    """Cross-platform advisory file lock using msvcrt on Windows and fcntl on Unix."""
    if IS_WINDOWS:
        import msvcrt
        mode = msvcrt.LK_NBLCK if non_blocking else msvcrt.LK_LOCK
        try:
            file_obj.seek(0)
            msvcrt.locking(file_obj.fileno(), mode, 1)
        except (OSError, IOError) as exc:
            raise BlockingIOError(str(exc)) from exc
        try:
            yield
        finally:
            try:
                file_obj.seek(0)
                msvcrt.locking(file_obj.fileno(), msvcrt.LK_UNLCK, 1)
            except (OSError, IOError):
                pass
    else:
        import fcntl
        flags = fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH
        if non_blocking:
            flags |= fcntl.LOCK_NB
        try:
            fcntl.flock(file_obj.fileno(), flags)
        except (BlockingIOError, OSError) as exc:
            raise BlockingIOError(str(exc)) from exc
        try:
            yield
        finally:
            try:
                fcntl.flock(file_obj.fileno(), fcntl.LOCK_UN)
            except OSError:
                pass


def terminate_process(process, timeout=8):
    """Terminate a process and its children cleanly across platforms."""
    if not process or process.poll() is not None:
        return
    try:
        if IS_WINDOWS:
            try:
                subprocess.run(
                    ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                    capture_output=True,
                    check=False,
                )
            except Exception:
                process.terminate()
            process.wait(timeout=timeout)
        else:
            if hasattr(os, "killpg"):
                os.killpg(process.pid, signal.SIGTERM)
            else:
                process.terminate()
            process.wait(timeout=timeout)
    except (subprocess.TimeoutExpired, Exception):
        try:
            if IS_WINDOWS:
                process.kill()
            else:
                if hasattr(os, "killpg") and hasattr(signal, "SIGKILL"):
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
        except (ProcessLookupError, OSError):
            pass


def resolve_asset_path(app_dir, relative_path):
    """Resolve an asset path, handling Windows Git symlink text stubs for 'models'."""
    p = app_dir / relative_path
    if p.is_file():
        return p
    rel_str = str(relative_path).replace("\\", "/")
    if rel_str.startswith("models/"):
        models_stub = app_dir / "models"
        if models_stub.is_file():
            target_dir = (app_dir / models_stub.read_text(encoding="utf-8").strip()).resolve()
            subpath = rel_str[len("models/"):]
            candidate = target_dir / subpath
            return candidate
    return p
