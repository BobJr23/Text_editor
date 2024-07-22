import PySimpleGUI as sg
import os


def main():
    filename = None
    sg.theme('Darkblue')
    sg.set_options(font=('Courier New', 15))

    layout = [
        [sg.Menu([["File", ["Open", "Save", "Save As", "Close file", "Exit"]]])],
        [],
        [sg.Multiline("Choose a file to begin", key="text", expand_x=True, expand_y=True)],
    ]

    window = sg.Window("BobJr editor", layout, resizable=True).Finalize()
    window.maximize()
    while True:
        event, values = window.read()
        print(event, values)
        match event:
            case sg.WIN_CLOSED:
                break

            case "Open":
                filename = sg.popup_get_file("Select a file", no_window=True)
                with open(filename) as f:
                    text = f.read()
                    window["text"].update(text)
                    f.close()

            case "Save":
                with open(filename, "w") as f:
                    f.write(values["text"])
                    f.close()

            case "Save As":
                with open(filename, "w") as f:
                    f.write(values["text"])
                    f.close()
                os.rename(filename, sg.popup_get_file(
                    "Select a file", save_as=True, no_window=True,
                    )
                )

            case "Close file":
                filename = None
                window["text"].update("")

            case "Exit":
                break

    window.close()


if __name__ == "__main__":
    main()
