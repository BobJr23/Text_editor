import PySimpleGUI as sg


def main():
    filename = None
    sg.theme('Darkblue')
    sg.set_options(font=('Courier New', 15))

    layout = [
        [sg.Menu([["File", ["Open", "Save"]]])],
        [sg.Multiline("Choose a file to begin", key="text", expand_x=True, expand_y=True)],
    ]

    window = sg.Window("BobJr editor", layout, resizable=True).Finalize()
    window.maximize()
    while True:
        event, values = window.read()
        print(event, values)
        if event == sg.WIN_CLOSED:
            break
        elif event == "Open":
            filename = sg.popup_get_file("Select a file")
            with open(filename) as f:
                text = f.read()
                window["text"].update(text)
        elif event == "Save":
            with open(filename, "w") as f:
                f.write(values["text"])

    window.close()


if __name__ == "__main__":
    main()
