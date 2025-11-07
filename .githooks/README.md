# Git Hooks

This directory contains custom Git hooks for the repository.

## Setup

To enable these hooks, run from the repository root:

```bash
git config core.hooksPath .githooks
```

## Available Hooks

### pre-commit

Prevents committing legacy brand tokens (old internal names or deprecated brand identifiers).

**Requirements:**
- Python 3 must be installed and on your PATH

**How it works:**
1. Runs automatically before each commit
2. Checks all staged files for configured legacy tokens
3. Blocks the commit if any tokens are found
4. Shows which files and lines contain the tokens

**Manual execution:**
```bash
python app/scripts/check_no_legacy_brand.py --staged
```

## Adding Legacy Tokens

To add tokens that should be blocked from commits:

1. Edit `app/scripts/check_no_legacy_brand.py`
2. Add patterns to the `LEGACY_PATTERNS` list
3. Tokens are checked case-insensitively

Example:
```python
LEGACY_PATTERNS = [
    re.compile(p, re.IGNORECASE) for p in [
        r"market\s*wiz",
        r"marketwiz",
        r"OldBrandName",
    ]
]
```

## Bypassing Hooks (Emergency Only)

If you absolutely must commit without running hooks:

```bash
git commit --no-verify -m "Your message"
```

**Warning:** Only use this in emergencies. The hooks exist to protect code quality.
