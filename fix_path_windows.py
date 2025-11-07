import os

# Common directories to add to PATH
COMMON_PATHS = [
    r"C:\\Windows\\System32",
    r"C:\\Windows",
    r"C:\\Windows\\System32\\Wbem",
    r"C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\",
    os.path.expanduser(r"~\\AppData\\Local\\Programs\\Python\\Python3x\\Scripts"),
    os.path.expanduser(
        r"~\\AppData\\Local\\Packages\\PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0\\LocalCache\\local-packages\\Python313\\Scripts"
    ),
]


def get_current_path():
    return os.environ.get("PATH", "")


def add_to_path(paths):
    current_path = get_current_path()
    path_list = current_path.split(os.pathsep)
    added = False
    for p in paths:
        if p and p not in path_list and os.path.exists(p):
            path_list.append(p)
            print(f"Added to PATH: {p}")
            added = True
    if added:
        new_path = os.pathsep.join(path_list)
        os.environ["PATH"] = new_path
        print("PATH updated for this session.")
        print(
            "To make this permanent, add these folders to your system/user PATH environment variable."
        )
    else:
        print("No new valid paths added. PATH is already set or folders do not exist.")


def main():
    print("Current PATH:")
    print(get_current_path())
    print("\nChecking and adding common directories...")
    add_to_path(COMMON_PATHS)


if __name__ == "__main__":
    main()
