#!/usr/bin/env python3
"""
Check for legacy brand tokens in code.

This script prevents accidentally committing old internal names or legacy brand tokens
into the repository. It can be used as a standalone script or as part of a git pre-commit hook.

Usage:
    python scripts/check_no_legacy_brand.py --staged    # Check staged files (for git hook)
    python scripts/check_no_legacy_brand.py             # Check all tracked files
"""

import sys
import subprocess
import re
import argparse
from pathlib import Path


# List of legacy brand tokens to check for (case-insensitive)
# Add old internal names, codenames, or deprecated brand names here
LEGACY_TOKENS = [
    # Example: "OldBrandName",
    # Example: "InternalCodeName",
    # Add tokens as needed when rebranding or renaming
]

# File patterns to exclude from checking
EXCLUDE_PATTERNS = [
    r'\.git/',
    r'node_modules/',
    r'\.venv/',
    r'venv/',
    r'__pycache__/',
    r'\.pyc$',
    r'package-lock\.json',
    r'yarn\.lock',
    r'\.min\.js$',
    r'\.min\.css$',
    r'dist/',
    r'build/',
    r'coverage/',
    r'test-results/',
    r'\.pytest_cache/',
    # Don't check this script itself
    r'scripts/check_no_legacy_brand\.py$',
]

# Text file extensions to check
TEXT_EXTENSIONS = {
    '.py', '.js', '.jsx', '.ts', '.tsx', '.json', '.md', '.txt',
    '.html', '.css', '.scss', '.yaml', '.yml', '.sh', '.bash'
}

# Specific filenames to check (extensionless or template files)
SPECIAL_FILENAMES = {
    '.gitignore',
    'Dockerfile',
    'README',
    '.env.example',
    '.env.template'
}


def should_check_file(filepath):
    """Determine if a file should be checked for legacy tokens."""
    filepath_str = str(filepath)
    
    # Check exclude patterns
    for pattern in EXCLUDE_PATTERNS:
        if re.search(pattern, filepath_str):
            return False
    
    # Check if file has a text extension
    if filepath.suffix in TEXT_EXTENSIONS:
        return True
    
    # Check for specific extensionless or template files
    if filepath.name in SPECIAL_FILENAMES:
        return True
    
    return False


def get_staged_files():
    """Get list of staged files from git."""
    try:
        result = subprocess.run(
            ['git', 'diff', '--cached', '--name-only', '--diff-filter=ACMR'],
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.strip().split('\n')
        return [Path(f) for f in files if f]
    except subprocess.CalledProcessError:
        print("Error: Could not get staged files. Are you in a git repository?", file=sys.stderr)
        sys.exit(1)


def get_all_tracked_files():
    """Get list of all tracked files from git."""
    try:
        result = subprocess.run(
            ['git', 'ls-files'],
            capture_output=True,
            text=True,
            check=True
        )
        files = result.stdout.strip().split('\n')
        return [Path(f) for f in files if f]
    except subprocess.CalledProcessError:
        print("Error: Could not get tracked files. Are you in a git repository?", file=sys.stderr)
        sys.exit(1)


def check_file(filepath):
    """Check a single file for legacy tokens. Returns list of (line_num, line_text, token) tuples."""
    violations = []
    
    if not filepath.exists():
        return violations
    
    # Pre-compile regex patterns for better performance
    compiled_patterns = [
        (token, re.compile(re.escape(token), re.IGNORECASE))
        for token in LEGACY_TOKENS
    ]
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            for line_num, line in enumerate(f, start=1):
                for token, pattern in compiled_patterns:
                    if pattern.search(line):
                        violations.append((line_num, line.rstrip(), token))
    except (IOError, OSError) as e:
        # Skip files that can't be read (e.g., permission denied, binary files)
        # Silently skip as these are typically not text files we care about
        pass
    except Exception as e:
        # Log unexpected errors but continue checking other files
        print(f"Warning: Could not check {filepath}: {e}", file=sys.stderr)
    
    return violations


def main():
    parser = argparse.ArgumentParser(
        description='Check for legacy brand tokens in code'
    )
    parser.add_argument(
        '--staged',
        action='store_true',
        help='Only check staged files (for use in git hooks)'
    )
    args = parser.parse_args()
    
    # Early exit if no legacy tokens are configured
    if not LEGACY_TOKENS:
        print("✓ No legacy brand tokens configured to check.")
        sys.exit(0)
    
    # Get files to check
    if args.staged:
        files = get_staged_files()
        scope = "staged files"
    else:
        files = get_all_tracked_files()
        scope = "tracked files"
    
    # Filter to only files we should check
    files_to_check = [f for f in files if should_check_file(f)]
    
    # Check each file
    all_violations = {}
    for filepath in files_to_check:
        violations = check_file(filepath)
        if violations:
            all_violations[filepath] = violations
    
    # Report results
    if all_violations:
        print(f"❌ Found legacy brand tokens in {scope}:\n", file=sys.stderr)
        for filepath, violations in all_violations.items():
            print(f"  {filepath}:", file=sys.stderr)
            for line_num, line_text, token in violations:
                print(f"    Line {line_num}: '{token}' found", file=sys.stderr)
                print(f"      {line_text}", file=sys.stderr)
        print(f"\n❌ Commit blocked. Please remove legacy brand tokens before committing.", file=sys.stderr)
        sys.exit(1)
    else:
        print(f"✓ No legacy brand tokens found in {scope}.")
        sys.exit(0)


if __name__ == '__main__':
    main()
