import PySimpleGUI as sg
import os


def main():
    filename = None
    sg.theme('Darkblue')
    sg.set_options(font=('Courier New', 15))

    layout = [
        [sg.Menu([["File", ["Open", "Save", "Save As", "Close file", "Exit"]]])],
        [sg.Listbox(values=[], enable_events=True, size=(None, 3), key="listbox", expand_x=True, sbar_width=3,
                    sbar_arrow_width=3, sbar_trough_color=None,)],
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
                current_files = window["listbox"].get_list_values()

                current_files.append(filename)
                window["listbox"].update(current_files)

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

                current_files = window["listbox"].get_list_values()

                current_files.pop(current_files.index(values["listbox"][0]))
                window["listbox"].update(current_files)
                window["text"].update("")

            case "listbox":
                filename = values["listbox"][0]
                if filename != "":
                    with open(filename) as f:
                        text = f.read()
                        window["text"].update(text)
                        f.close()

            case "Exit":
                break

    window.close()


if __name__ == "__main__":
    main()
