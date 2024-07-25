import subprocess
import os


def run(arg, element=None, start=os.getcwd(), opencommand=False):
    if opencommand:
        os.system(f"start cmd /k {" ".join(arg)}")
    else:
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
            # print("Done!")
            element.update(value="\n" + "Process finished", append=True)
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


def test_to_cmd():

    process = subprocess.Popen(
        ["cmd", "/k"],
        shell=True,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=None,
    )
    # passing command
    stdOutput, stdError = process.communicate(input="date /t".encode())
    print(stdOutput)
    input("Press Enter to exit...")
    process.stdin.close()


if __name__ == "__main__":
    # run("date /t".split(), opencommand=True)
    test_to_cmd()
