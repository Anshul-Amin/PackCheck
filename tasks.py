"""Cross-platform task runner for PackCheck (Windows, macOS, Linux).

Usage:
    python tasks.py setup   # Install requirements
    python tasks.py test    # Run full test suite
    python tasks.py run     # Launch Streamlit web UI
    python tasks.py demo    # Warm cache and launch UI
    python tasks.py eval    # Run CLI accuracy evaluation
    python tasks.py lint    # Run ruff check and format check
"""

import subprocess
import sys


def run_command(cmd: list[str]) -> int:
    print(f"Executing: {' '.join(cmd)}")
    return subprocess.run(cmd).returncode


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(0)

    task = sys.argv[1].lower()

    if task == "setup":
        code = run_command([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        sys.exit(code)

    elif task == "test":
        code = run_command([sys.executable, "-m", "pytest", "tests/", "-v"])
        sys.exit(code)

    elif task == "run":
        code = run_command([sys.executable, "-m", "streamlit", "run", "app/streamlit_app.py"])
        sys.exit(code)

    elif task == "demo":
        run_command([sys.executable, "scripts/demo_cache_warm.py"])
        code = run_command([sys.executable, "-m", "streamlit", "run", "app/streamlit_app.py"])
        sys.exit(code)

    elif task == "eval":
        code = run_command([sys.executable, "scripts/run_cli.py", "--eval"])
        sys.exit(code)

    elif task == "lint":
        code1 = run_command([sys.executable, "-m", "ruff", "check", "."])
        code2 = run_command([sys.executable, "-m", "ruff", "format", "--check", "."])
        sys.exit(code1 or code2)

    else:
        print(f"Unknown task: {task}\n")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
