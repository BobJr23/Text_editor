import subprocess
import os


def run(file_path, start=os.getcwd(), interpreter="python", element=None):

    if os.path.exists(file_path):
        print("Running!")
        process = subprocess.Popen(
            [interpreter, file_path],
            cwd=start,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                element.update(value=line, append=True)

    else:
        print("File not found")
        return
