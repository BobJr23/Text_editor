import PySimpleGUI as sg
import os
import tkinter


# modified https://github.com/PySimpleGUI/PySimpleGUI/issues/2437
def update_theme(window: sg.Window, selected_theme):
    current_them = sg.LOOK_AND_FEEL_TABLE[selected_theme]

    try:
        window_bkg = current_them.get("BACKGROUND")
        window.TKroot.config(background=window_bkg)
    except Exception as e:
        print(e)

        # iterate over all widgets:
    print(current_them)
    for v, element in window.AllKeysDict.items():

        try:

            if element.Type == "button":
                color = current_them.get("BUTTON")
                background = current_them.get("SCROLL")
                element.Widget.config(foreground=color[0], background=background)
            elif element.Type in ["listbox", "multiline"]:
                color = current_them.get("INPUT")
                element.Widget.config(background=color)

            else:
                color = current_them.get("BACKGROUND")
                element.Widget.config(background=color)

            element.update()

        except Exception as e:
            print(e)


def main():
    filename = None
    sg.theme("DarkBlue3")

    sg.set_options(font=("Courier New", 15))

    layout = [
        [
            sg.Menu(
                [
                    [
                        "File",
                        ["Open", "Save", "Save As", "Close file", "---", "Exit editor"],
                    ],
                    ["Theme", ["Preview themes", "Choose theme"]],
                ]
            )
        ],
        [
            sg.Listbox(
                values=[],
                enable_events=True,
                size=(None, 3),
                key="listbox",
                expand_x=True,
                sbar_width=3,
                sbar_arrow_width=3,
            )
        ],
        [
            sg.Multiline(
                "Choose a file to begin", key="text", expand_x=True, expand_y=True
            )
        ],
    ]

    window = sg.Window("BobJr editor", layout, resizable=True, finalize=True)
    window.maximize()
    while True:
        event, values = window.read()
        print(event, values)
        match event:
            case sg.WIN_CLOSED:
                break

            case "Open":
                filename = sg.popup_get_file("Select a file", no_window=True)
                if filename is not None:
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
                os.rename(
                    filename,
                    sg.popup_get_file(
                        "Select a file",
                        save_as=True,
                        no_window=True,
                    ),
                )

            case "Close file":

                current_files = window["listbox"].get_list_values()

                current_files.pop(current_files.index(values["listbox"][0]))
                window["listbox"].update(current_files)
                window["text"].update("")

            case "listbox":
                try:
                    filename = values["listbox"][0]
                except IndexError:
                    continue
                with open(filename) as f:
                    text = f.read()
                    window["text"].update(text)
                    f.close()

            case "Preview themes":
                sg.theme_previewer(scrollable=True, columns=6)

            case "Choose theme":
                window.disable()
                theme = None
                window2 = sg.Window(
                    "Choose a theme",
                    [
                        [
                            sg.Input(
                                focus=True,
                                tooltip="Search for a theme",
                                key="theme-input",
                                enable_events=True,
                                size=(20, 1),
                            )
                        ],
                        [
                            sg.Listbox(
                                values=sg.theme_list(),
                                key="theme",
                                size=(20, 20),
                                expand_y=True,
                                enable_events=True,
                            ),
                            sg.Text("Example Text", size=(20, 1)),
                            sg.Button("Example Button, size=(20, 1)"),
                            sg.Input(default_text="Example Input", size=(20, 1)),
                            sg.Multiline("Example Multiline", size=(20, 20)),
                        ],
                        [sg.Button("Submit")],
                    ],
                    resizable=True,
                    finalize=True,
                )
                window2.maximize()

                current_them = sg.LOOK_AND_FEEL_TABLE[sg.theme()]
                window_bkg = current_them.get("BACKGROUND")
                while True:
                    event2, values2 = window2.read()
                    print(event2, values2)
                    if event2 in (sg.WIN_CLOSED, "Submit"):
                        break
                    if event2 == "theme":
                        theme = values2["theme"][0]
                        update_theme(window2, theme)

                    if event2 == "theme-input":
                        window2["theme"].update(
                            [
                                i
                                for i in sg.theme_list()
                                if values2["theme-input"].lower() in i.lower()
                            ]
                        )

                window2.close()

                window.enable()

            case "Exit editor":
                break

    window.close()


if __name__ == "__main__":
    main()
