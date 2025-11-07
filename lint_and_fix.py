#!/usr/bin/env python3
"""
Comprehensive linting and fixing script for CrossPostMe project.
Runs ruff linter, applies automatic fixes, and reports issues.
"""
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and return exit code, stdout, stderr."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
        )
        return result.returncode, result.stdout, result.stderr
    except FileNotFoundError:
        print(f"ERROR: Command not found: {cmd[0]}")
        print("Please ensure all linting tools are installed:")
        print("  pip install ruff")
        return 1, "", f"Command not found: {cmd[0]}"


def main():
    """Main linting and fixing workflow."""
    project_root = Path(__file__).parent
    app_backend = project_root / "app" / "backend"

    print(f"Project root: {project_root}")
    print(f"Backend path: {app_backend}")

    if not app_backend.exists():
        print(f"ERROR: Backend directory not found: {app_backend}")
        return 1

    all_passed = True

    # 1. Ruff format check (dry run)
    print("\n" + "=" * 60)
    print("STEP 1: Checking code formatting with ruff")
    print("=" * 60)
    code, stdout, stderr = run_command(
        ["ruff", "format", "--check", str(app_backend)], "Ruff format check (dry run)"
    )
    if code != 0:
        print("WARNING: Formatting issues found. Running auto-fix...")
        code2, stdout2, stderr2 = run_command(
            ["ruff", "format", str(app_backend)], "Ruff format auto-fix"
        )
        if code2 == 0:
            print("SUCCESS: Formatting fixed automatically")
        else:
            print("ERROR: Formatting fix failed")
            print(stdout2)
            print(stderr2)
            all_passed = False
    else:
        print("SUCCESS: Code formatting looks good")

    # 2. Ruff lint check
    print("\n" + "=" * 60)
    print("STEP 2: Running ruff linter")
    print("=" * 60)
    code, stdout, stderr = run_command(
        ["ruff", "check", str(app_backend), "--output-format=text"], "Ruff lint check"
    )
    if code != 0:
        print("WARNING: Linting issues found:")
        print(stdout)
        if stderr:
            print(stderr)

        print("\n" + "-" * 60)
        print("Attempting automatic fixes...")
        print("-" * 60)
        code2, stdout2, stderr2 = run_command(
            ["ruff", "check", str(app_backend), "--fix"], "Ruff lint auto-fix"
        )

        # Check if issues remain after auto-fix
        code3, stdout3, stderr3 = run_command(
            ["ruff", "check", str(app_backend), "--output-format=text"],
            "Ruff lint re-check",
        )
        if code3 != 0:
            print("WARNING: Some issues remain after auto-fix:")
            print(stdout3)
            all_passed = False
        else:
            print("SUCCESS: All lint issues fixed automatically")
    else:
        print("SUCCESS: No linting issues found")

    # 3. Summary
    print("\n" + "=" * 60)
    print("LINTING SUMMARY")
    print("=" * 60)
    if all_passed:
        print("SUCCESS: All checks passed! Code is clean.")
        return 0
    else:
        print("WARNING: Some issues require manual attention.")
        print("\nTo see detailed issues, run:")
        print(f"  cd {app_backend}")
        print("  ruff check . --output-format=text")
        return 1


if __name__ == "__main__":
    sys.exit(main())
