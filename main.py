import random
import time
import PySimpleGUI as sg
import json
import re
from highlighter import do_highlighting, styles
import os
from run_file import run
import threading


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


def load_from_file(filename, window: sg.Window, tab_dict, add_to_tab=True, update=True):
    if update:
        with open(filename) as f:
            text = f.read()

            do_highlighting(window, text)

            f.close()
        update_lines(window, text)

    if add_to_tab:
        window["TabGroup"].add_tab(
            sg.Tab(title=os.path.basename(filename), layout=[[]])
        )
        window["TabGroup"].Widget.select(len(tab_dict) - 1)
        tab_dict["current_tab"] = len(tab_dict) - 1
        tab_dict[os.path.basename(filename)] = filename
    else:
        tab_dict["current_tab"] = (
            list(tab_dict.keys()).index(os.path.basename(filename)) - 1
        )
    window["path"].update(f"{os.path.dirname(filename)}>")

    print(filename)
    return tab_dict


def save_settings(open_files, settings):
    with open("settings.json", "w") as f:
        f.write(
            json.dumps(
                {
                    "theme": sg.theme(),
                    "open_files": open_files,
                    "interpreter": settings["interpreter"],
                }
            )
        )
        f.close()


def load_settings():
    with open("settings.json") as f:
        settings = json.load(f)
        f.close()
    return settings


def update_lines(window: sg.Window, text: str):
    lines = text.count("\n") + 1
    window["numbers"].update("\n".join([str(x) for x in range(1, lines + 2)]))
    window["numbers"].TKText.yview_moveto(window["text"].TKText.yview()[0])


def drag_scroll(event, window):
    window["numbers"].TKText.yview_moveto(window["text"].TKText.yview()[0])


def highlight_line(window: sg.Window, cursor_pos):
    pass


def main():
    filename = None
    settings = load_settings()
    Tab_dict = {"current_tab": None}
    sg.theme(settings["theme"])
    sg.theme_input_background_color("#282c34")

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
                    [
                        "Run",
                        [
                            "Select interpreter",
                            "Run file",
                            "---",
                            "Run file in Command Prompt",
                            "Open Command Prompt",
                        ],
                    ],
                ]
            ),
        ],
        [
            sg.TabGroup([[]], key="TabGroup", enable_events=True, expand_x=True),
            sg.Input(
                visible=False, enable_events=True, key="find_input", tooltip="Find"
            ),
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
                default_text="1\n2\n3\n4\n5\n6\n7\n8\n9\n10",
                key="numbers",
                size=(4, 0),
                disabled=True,
                no_scrollbar=True,
                expand_y=True,
                expand_x=False,
                pad=(1, 0),
            ),
            sg.Multiline(
                "Choose a file to begin",
                key="text",
                size=(190, 35),
                enable_events=True,
                expand_y=True,
                pad=(0, 0),
                rstrip=False,
                selected_background_color="#404859",
            ),
        ],
        [
            sg.Button(
                ".",
                key="resize",
                tooltip="Resize",
                enable_events=True,
                size=(0, 1),
                expand_x=True,
                pad=(0, 0),
            )
        ],
        [
            sg.Multiline(
                visible=True,
                key="terminal",
                default_text="Terminal output",
                expand_x=True,
                expand_y=True,
                autoscroll=True,
                disabled=True,
            ),
        ],
        [
            sg.Multiline(
                default_text=os.getcwd() + ">",
                key="path",
                disabled=True,
                visible=True,
                size=(70, 2),
            ),
            sg.Multiline(
                visible=True, key="terminal_input", expand_x=True, size=(0, 2)
            ),
        ],
    ]

    window = sg.Window("BobJr editor", layout, resizable=True, finalize=True)
    window.maximize()
    window.bind("<Control-s>", "Save_bind")
    window.bind("<Control-o>", "Open_bind")
    window.bind("<Control-w>", "Close_bind")
    window.bind("<Control-f>", "Find")
    window["find_input"].bind("<Return>", "_occurrence")
    window["find_input"].bind("<Escape>", "_close_find")
    window["terminal_input"].bind("<Return>", "_run")
    window["text"].bind("<MouseWheel>", "_scroll")
    window["text"].bind("<Key>", "_text")
    window["text"].vsb.bind("<B1-Motion>", lambda e: drag_scroll(e, window))
    window["text"].bind("<Button-1>", "_click")
    window["numbers"].bind("<MouseWheel>", "_scroll")
    window["text"].Widget.tag_config(
        "normal", foreground=styles["normal"]["text_color"]
    )

    for pattern_name in styles:
        window["text"].Widget.tag_config(
            pattern_name, foreground=styles[pattern_name]["text_color"]
        )
    window["text"].Widget.tag_config("current", background="#30343c")
    window["text"].Widget.tag_config("find", background="orange", foreground="white")
    try:
        for x in settings["open_files"]:
            Tab_dict = load_from_file(x, window, Tab_dict, update=False)
    except KeyError:
        pass
    while True:
        event, values = window.read()
        print(event, values)
        match event:
            case sg.WIN_CLOSED:
                break

            case "Open" | "Open_bind":
                filename = sg.popup_get_file("Select a file", no_window=True)
                if filename is not None:
                    Tab_dict = load_from_file(filename, window, Tab_dict)

            case "Save" | "Save_bind":
                with open(filename, "w") as f:
                    f.write(values["text"])
                    f.close()
                do_highlighting(window, values["text"])
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
                current_tab = Tab_dict["current_tab"]
                if current_tab:
                    window["TabGroup"].Widget.forget(current_tab)
                    window["text"].update("")

            case "TabGroup":
                try:
                    filename = values["TabGroup"]
                except IndexError:
                    print("index error")
                    continue
                Tab_dict = load_from_file(
                    Tab_dict[filename], window, Tab_dict, add_to_tab=False
                )
                window["text"].TKText.see("1.0")

            case "Preview themes":
                sg.theme_previewer(scrollable=True, columns=6)

            case "Find":
                window["find_input"].update(visible=True)
                window["close_find"].update(visible=True)
                window["counter"].update(visible=True)
                window["find_input"].set_focus()

            case "text":
                cursor_pos = window["text"].Widget.index("insert")
                do_highlighting(window, values["text"], values["find_input"])
                window["text"].set_focus()
                window["text"].Widget.mark_set("insert", cursor_pos)
                update_lines(window, values["text"])

            case "text_scroll":
                update_lines(window, values["text"])

            case "numbers_scroll":
                window["text"].TKText.yview_moveto(window["numbers"].TKText.yview()[0])

            case "text_click":
                cursor_pos = window["text"].Widget.index("insert")
                window["text"].Widget.tag_remove("current", "1.0", "end")
                window["text"].Widget.tag_add(
                    "current",
                    cursor_pos + "linestart",
                    str(float(cursor_pos) + 1) + "linestart",
                )

            case "find_input":
                text = values["text"]
                search = values["find_input"].lower()
                if search != "":
                    count, first = do_highlighting(window, text, search)
                else:
                    count, first = do_highlighting(window, text)
                if count == 0:
                    window["counter"].update("0/0")
                else:
                    window["counter"].update("1/" + str(count))
                    window["text"].TKText.see(first)

            case "find_input_occurrence":
                occ_text = re.split(
                    values["find_input"].lower(),
                    values["text"],
                    flags=re.IGNORECASE,
                )

                occurrence = window["counter"].get().split("/")
                current = int(occurrence[0])
                total = int(occurrence[1])
                if current == "0":
                    continue
                elif current == total:
                    window["counter"].update("1/" + str(total))
                    window["text"].TKText.see(f"{occ_text[0].count('\n')}.0")
                else:
                    window["counter"].update(str(current + 1) + "/" + str(total))
                    window["text"].TKText.see(
                        f"{sum([x.count('\n') for x in occ_text[:(current + 1)]]) + 2}.0"
                    )

            case "close_find" | "find_input_close_find":
                window["find_input"].update(visible=False)
                window["counter"].update(visible=False)
                window["close_find"].update(visible=False)
                do_highlighting(window, values["text"])

            case "Select interpreter":
                interpreter = sg.popup_get_file("Select an interpreter", no_window=True)
                if interpreter is not None:
                    settings["interpreter"] = interpreter

            case "Run file":
                filename = values["TabGroup"]
                if filename not in [None, ""]:

                    if settings["interpreter"] in [None, ""]:
                        sg.popup("Please select an interpreter")
                        continue
                    if filename is None or not filename.endswith(".py"):
                        sg.popup("Please select a python file to run")
                        continue
                    window["terminal"].update(visible=True)
                    window["terminal"].update(f"{settings['interpreter']} {filename}\n")
                    threading.Thread(
                        target=run,
                        kwargs={
                            "arg": [settings["interpreter"], filename],
                            "start": values["path"].split(">")[0],
                            "element": window["terminal"],
                        },
                        daemon=True,
                    ).start()

            case "Run file in Command Prompt":
                run([settings["interpreter"], filename], opencommand=True)

            case "Open Command Prompt":
                os.system(f"start cmd /k")

            case "New":
                window["text"].update("")
                filename = sg.popup_get_file(
                    "Select a location to save to", no_window=True, save_as=True
                )
                Tab_dict = load_from_file(
                    filename, window, Tab_dict, add_to_tab=True, update=False
                )
                with open(filename, "w") as f:
                    f.write("")
                    f.close()

            case "terminal_input_run":
                window["text"].set_size((190, 5))
                window["terminal_input"].update("")
                window["terminal"].update(
                    values["path"] + values["terminal_input"] + "\n"
                )
                threading.Thread(
                    target=run,
                    kwargs={
                        "start": values["path"].split(">")[0],
                        "element": window["terminal"],
                        "arg": (values["terminal_input"].split()),
                    },
                    daemon=True,
                ).start()

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

    save_settings([tab for tab in Tab_dict.values() if isinstance(tab, str)], settings)
    window.close()


if __name__ == "__main__":
    FONT = "Jetbrains Mono"
    main()
