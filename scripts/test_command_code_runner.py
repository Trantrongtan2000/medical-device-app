import subprocess
import sys

sys.stdout.reconfigure(encoding='utf-8')

print("Testing command-code CLI invocation...")
try:
    res = subprocess.run(
        ["command-code.cmd", "--help"],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
        timeout=15,
        shell=True
    )
    print("Return Code:", res.returncode)
    print("STDOUT Preview:\n", res.stdout[:1000])
    if res.stderr:
        print("STDERR:\n", res.stderr[:500])
except Exception as e:
    print("Error:", e)
