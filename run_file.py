import subprocess
import os


def run(arg: tuple, element=None, start=os.getcwd()):

    process = subprocess.Popen(
        arg,
        cwd=start,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True,
    )

    if element:
        while True:
            line = process.stdout.readline()
            if not line and process.poll() is not None:
                break
            if line:
                element.update(value=line, append=True)
        process.wait()
        print("Done!")
        element.update(value="\n" + "Done!", append=True)
    else:
        while True:
            line = process.stdout.readline()
            line2 = process.stderr.readline()
            if not line and process.poll() is not None:
                break
            if line:
                print(line, end="")
            if line2:
                print(line2, end="")


if __name__ == "__main__":
    run("date /t".split())
