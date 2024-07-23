import PySimpleGUI as sg
import os
import tkinter
import json
import re


# modified https://github.com/PySimpleGUI/PySimpleGUI/issues/2437
def update_theme(window: sg.Window, selected_theme):
    if selected_theme is None:
        return
    current_them = sg.LOOK_AND_FEEL_TABLE[selected_theme]

    try:
        window_bkg = current_them.get("BACKGROUND")
        window.TKroot.config(background=window_bkg)
    except Exception as e:
        print(e)

        # iterate over all widgets:

    for v, element in window.AllKeysDict.items():

        try:

            if element.Type == "button":
                color = current_them.get("BUTTON")

                element.Widget.config(foreground=color[0], background=color[1])
            elif element.Type in ["listbox", "multiline", "input"]:
                color = current_them.get("INPUT")
                element.Widget.config(
                    background=color, foreground=current_them.get("TEXT_INPUT")
                )
            else:
                color = current_them.get("BACKGROUND")
                element.Widget.config(background=color)

            element.update()

        except Exception as e:
            print(e)


def load_from_file(filename, window: sg.Window, find=""):
    with open(filename) as f:
        text = f.read()
        window["text"].update(text)

        f.close()

    current_files = window["listbox"].get_list_values()
    current_files.append(filename)
    window["listbox"].update(current_files)


def save_settings(open_files):
    with open("settings.json", "w") as f:
        # implement files opened
        f.write(
            json.dumps(
                {
                    "theme": sg.theme(),
                    "open_files": open_files,
                }
            )
        )
        f.close()


def load_settings():
    with open("settings.json") as f:
        settings = json.load(f)
        f.close()
    return settings


def main():
    filename = None
    settings = load_settings()
    sg.theme(settings["theme"])

    # Upload ttf file to C:\Windows\Fonts folder
    sg.set_options(font=(FONT, 12))

    layout = [
        [
            sg.Menu(
                [
                    [
                        "File",
                        [
                            "Open",
                            "Save",
                            "Save As",
                            "Close file",
                            "---",
                            "New",
                            "---",
                            "Exit editor",
                        ],
                    ],
                    ["Theme", ["Preview themes", "Choose theme"]],
                    ["Edit", ["Find"]],
                ]
            ),
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
            ),
            sg.Input(visible=False, enable_events=True, key="find_input"),
            sg.Button(
                button_text="x",
                visible=False,
                key="close_find",
                font=(FONT, 6),
                size=(2, 2),
                pad=(0, 0),
            ),
            sg.Text("0", visible=False, key="counter"),
        ],
        [
            sg.Multiline(
                "Choose a file to begin", key="text", expand_x=True, expand_y=True
            )
        ],
    ]

    window = sg.Window("BobJr editor", layout, resizable=True, finalize=True)
    window.maximize()
    window.bind("<Control-s>", "Save_bind")
    window.bind("<Control-o>", "Open_bind")
    window.bind("<Control-w>", "Close_bind")
    window.bind("<Control-f>", "Find")
    for x in settings["open_files"]:
        load_from_file(x, window)
    while True:
        event, values = window.read()

        match event:
            case sg.WIN_CLOSED:
                break

            case "Open" | "Open_bind":
                filename = sg.popup_get_file("Select a file", no_window=True)
                if filename is not None:
                    load_from_file(filename, window)

            case "Save" | "Save_bind":
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

            case "Close file" | "Close_bind":

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

            case "Find":
                window["find_input"].update(visible=True)
                window["close_find"].update(visible=True)
                window["counter"].update(visible=True)
                window["find_input"].set_focus()

            case "find_input":

                text = values["text"]
                search = values["find_input"].lower()
                count = text.lower().count(search)
                window["text"].update("")
                for i, x in enumerate(text.split("\n")):
                    if search != "" and search in x.lower():
                        words = x.split(search)
                        for word in words[:-1]:
                            window["text"].print(word, end="")
                            window["text"].print(
                                search,
                                background_color="orange",
                                text_color="white",
                                end="",
                            )
                        window["text"].print(words[-1])

                    else:
                        window["text"].print(x)
                window["counter"].update("1/" + str(count))

            case "close_find":
                window["find_input"].update(visible=False)
                window["counter"].update(visible=False)
                window["close_find"].update(visible=False)
                window["text"].update(values["text"])
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
                update_theme(window, theme)
            case "Exit editor":
                break

    # save = sg.popup_yes_no("Do you want to save your changes?", title="Save changes")
    save_settings(window["listbox"].get_list_values())
    window.close()


if __name__ == "__main__":
    FONT = "Jetbrains Mono"
    main()