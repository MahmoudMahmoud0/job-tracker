import subprocess
import signal
import sys

PYTHON = sys.executable

processes = [
    subprocess.Popen([PYTHON, "manage.py", "runserver"]),
    subprocess.Popen([PYTHON, "manage.py", "qcluster"]),
]

try:
    for p in processes:
        p.wait()
except KeyboardInterrupt:
    for p in processes:
        p.send_signal(signal.SIGINT)

    for p in processes:
        p.wait()

    sys.exit(0)