import subprocess
import os


def run(*args, element=None, start=os.getcwd()):
    print(list(args))
    exit()
    print("Running!")
    process = subprocess.Popen(
        list(args),
        cwd=start,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
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
            if not line and process.poll() is not None:
                break
            if line:
                print(line, end="")


if __name__ == "__main__":
    # run("ls", "test", "chat")
    os.system("dir")
