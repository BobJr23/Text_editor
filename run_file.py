import subprocess
import os


def run(file_path, start=os.path.abspath(__file__), interpreter="python"):

    if os.path.exists(file_path):
        t = subprocess.run(
            [interpreter, file_path], cwd=start, capture_output=True, text=True
        )

    else:
        print("File not found")
        return
    return t
