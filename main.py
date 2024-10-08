import json
import re
from helpers.highlighter import do_highlighting, styles, tk
import os
from helpers.run_file import run
import threading
from helpers.theme_maker import theme_selector, sg, create_theme_customizer
from helpers.google_ai import send_message_to_ai


def load_from_file(
    filename, window: sg.Window, tab_dict, add_to_tab=True, update=True, values=None
):
    if update:
        try:
            with open(filename) as f:
                text = f.read()

                do_highlighting(window, text, values=values)

                f.close()
        except FileNotFoundError:
            return tab_dict
        update_lines(window, text)

    if add_to_tab and filename not in tab_dict.values():
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
    window["path"].update(f"{os.path.dirname(filename).replace('/', "\\")}>")

    return tab_dict


def save_settings(open_files, settings, folder):
    with open("settings.json", "w") as f:
        f.write(
            json.dumps(
                {
                    "theme": sg.theme(),
                    "custom_theme": settings["custom_theme"],
                    "open_files": open_files,
                    "interpreter": settings["interpreter"],
                    "save_folder": folder,
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
    lines = text.count("\n")
    window["numbers"].update("\n".join([str(x) for x in range(1, lines + 1)]))
    window["numbers"].TKText.yview_moveto(window["text"].TKText.yview()[0])


def drag_scroll(window):
    window["numbers"].TKText.yview_moveto(window["text"].TKText.yview()[0])


def resize_top(window: sg.Window, y):
    window["text"].set_size((MULTILINE_WIDTH - 90, y))
    window["numbers"].set_size((4, y))
    window["folders"].set_size((1, y))
    window["copilot"].set_size((90, y - 3))


def find_text(text_widget: tk.Text, find, match_case, whole_word, find_all=False):
    text_widget.tag_remove("find", "1.0", tk.END)
    start_pos = "1.0"
    if not match_case:
        find = find.lower()
    while True:

        start_pos = text_widget.search(
            find, start_pos, tk.END, nocase=not match_case, regexp=whole_word
        )

        if not start_pos:
            break
        end_pos = f"{start_pos}+{len(find)}c"

        if whole_word:

            if not (
                text_widget.get(f"{start_pos}-1c").isspace()
                and text_widget.get(end_pos).isspace()
            ):
                start_pos = end_pos
                continue

        text_widget.tag_add("find", start_pos, end_pos)

        text_widget.mark_set(tk.INSERT, end_pos)
        text_widget.see(tk.INSERT)
        start_pos = end_pos
        if not find_all:
            return True
    return False


def find_and_replace(window, v):
    layout = [
        [sg.Text("Find:"), sg.Input(key="-FIND-", default_text=v["find_input"])],
        [sg.Text("Replace:"), sg.Input(key="-REPLACE-")],
        [sg.Checkbox("Match case", key="-MATCH_CASE-")],
        [sg.Checkbox("Whole word", key="-WHOLE_WORD-")],
        [
            sg.Button("Find"),
            sg.Button("Find all"),
            sg.Button("Replace"),
            sg.Button("Replace All"),
            sg.Button("Close"),
        ],
    ]

    search_window = sg.Window("Search and Replace", layout, modal=True)

    text_widget = window["text"].Widget

    while True:
        event, values = search_window.read()

        if event in (sg.WINDOW_CLOSED, "Close"):
            break

        find = values["-FIND-"]
        replace_text = values["-REPLACE-"]
        match_case = values["-MATCH_CASE-"]
        whole_word = values["-WHOLE_WORD-"]

        if event == "Find":
            find_text(text_widget, find, match_case, whole_word)

        if event == "Find all":
            find_text(text_widget, find, match_case, whole_word, find_all=True)

        elif event == "Replace":
            find_text(text_widget, find, match_case, whole_word)
            t = text_widget.tag_ranges("find")
            if t:
                text_widget.delete(t[0], t[1])
                text_widget.insert(tk.INSERT, replace_text)

        elif event == "Replace All":

            t = text_widget.tag_ranges("find")
            if t:
                for start, end in zip(
                    t[::2],
                    t[1::2],
                ):

                    text_widget.delete(start, end)
                    text_widget.insert(tk.INSERT, replace_text)
                sg.popup("Replaced " + str(len(t) // 2) + " occurrences")
    search_window.close()


def recurse_folder(folder, tree_data=sg.TreeData()):
    tree_data.insert(
        "",
        folder,
        folder.split("/")[-1] + " - " + (folder[-28:] if len(folder) > 27 else folder),
        [],
        icon="images/folder.png",
    )
    for file in os.listdir(folder):
        if os.path.isfile(folder + "/" + file):
            tree_data.insert(folder, file, file, [])
    for root, _, files in os.walk(folder):
        if root != folder:
            tree_data.insert(
                os.path.dirname(root),
                root,
                " " + root.split("\\")[-1],
                [],
                icon="images/folder.png",
            )
            for file in files:
                tree_data.insert(
                    root,
                    file,
                    " " + file,
                    [],
                    icon=("images/python.png" if file.endswith(".py") else "images/file.png"),
                )

    return tree_data


def main():
    filename = None
    settings = load_settings()

    Tab_dict = {"current_tab": 0}
    sg.LOOK_AND_FEEL_TABLE[settings["theme"]] = settings["custom_theme"]
    sg.theme(settings["theme"])
    sg.set_options(font=(FONT, 11))
    save_folder = None
    find_case = False
    if settings["save_folder"] is not None:
        tree_data = recurse_folder(settings["save_folder"])
        save_folder = settings["save_folder"]
    else:
        tree_data = sg.TreeData()
    keybinds = {
        "<Control-s>": "Save_bind",
        "<Control-o>": "Open_bind",
        "<Control-w>": "Close_bind",
        "<Control-f>": "Find",
        "<Control-t>": "New_bind",
        "<Control-r>": "Run_file",
        "<Control-q>": "Exit_editor",
    }
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
                            "New",
                            "---",
                            "Open folder",
                            "---",
                            "Exit editor",
                        ],
                    ],
                    [
                        "Theme",
                        [
                            "Preview built-in themes",
                            "Choose built-in theme",
                            "Customize theme",
                        ],
                    ],
                    ["Edit", ["Find", "Find and Replace", "Update keybinds"]],
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
                    [
                        "AI",
                        [
                            "Open AI Chat",
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
                button_text="Aa",
                visible=False,
                key="case",
                font=(FONT, 6),
                size=(2, 2),
                pad=(0, 0),
            ),
            sg.Button(
                button_text="x",
                visible=False,
                key="close_find",
                font=(FONT, 6),
                size=(2, 2),
                pad=(0, 0),
            ),
            sg.Button("Replace", visible=False, key="replace"),
            sg.Text("0", visible=False, key="counter"),
        ],
        [
            sg.Tree(
                tree_data,
                key="folders",
                headings=[],
                col0_heading="---Folders---",
                num_rows=20,
                col0_width=40,
                expand_x=False,
                enable_events=True,
                selected_row_colors=("white", "#61afef"),
                hide_vertical_scroll=True,
            ),
            sg.Multiline(
                default_text="1\n2\n3\n4\n5\n6\n7\n8\n9\n10",
                key="numbers",
                size=(4, 20),
                disabled=True,
                no_scrollbar=True,
                # expand_y=True,
                expand_x=False,
                pad=(1, 0),
            ),
            sg.Multiline(
                "Choose a file to begin",
                key="text",
                size=(MULTILINE_WIDTH, 20),
                enable_events=True,
                # expand_y=True,
                expand_x=True,
                pad=(0, 0),
                rstrip=False,
                selected_background_color="#404859",
            ),
            sg.Button("Copilot\nChat", key="Open AI Chat_b"),
            sg.Column(
                [
                    [
                        sg.Multiline(
                            key="copilot",
                            default_text="Copilot Chat\n",
                            size=(90, 18),
                            pad=(0, 0),
                            rstrip=False,
                            disabled=True,
                            reroute_cprint=True,
                        ),
                    ],
                    [
                        sg.Input(key="copilot_input", size=(64, 3), pad=(0, 0)),
                        sg.Checkbox("Include File", key="include_file"),
                        sg.Button("Close Chat", key="close_chat"),
                    ],
                ],
                visible=False,
                key="copilot_column",
            ),
        ],
        [
            sg.Button(
                "-----------Right Click to Hide | Double Left Click to Show | Drag to Extend/Hide Terminal------------",
                key="resize",
                tooltip="Resize",
                enable_events=True,
                # size=(0, 1),
                expand_x=True,
                pad=(0, 0),
                button_color=("black", "#282c34"),
                # font=(FONT, 6),
            )
        ],
        [
            sg.Multiline(
                visible=True,
                key="terminal",
                default_text="Terminal output",
                size=(190, 17),
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

    for key, value in keybinds.items():
        window.bind(key, value)
    window["find_input"].bind("<Return>", "_occurrence")
    window["find_input"].bind("<Escape>", "_close_find")
    window["terminal_input"].bind("<Return>", "_run")
    window["text"].bind("<MouseWheel>", "_scroll")
    window["text"].bind("<Key>", "_text")
    window["text"].vsb.bind("<B1-Motion>", lambda e: drag_scroll(window))
    window["text"].vsb.bind("<MouseWheel>", lambda e: drag_scroll(window))
    window["text"].bind("<Button-1>", "_click")
    window["numbers"].bind("<MouseWheel>", "_scroll")
    window["resize"].bind("<B1-Motion>", "_")
    window["resize"].bind("<Button-3>", "_rightclick")
    window["resize"].bind("<Double-Button-1>", "_double")
    window["copilot_input"].bind("<Return>", "_enter")
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
            Tab_dict = load_from_file(
                x, window, Tab_dict, update=False, values={"TabGroup": x}
            )

    except KeyError:
        pass

    while True:
        event, values = window.read()
        # print(event, values)
        match event:
            case sg.WIN_CLOSED:
                break

            case "Open" | "Open_bind":
                filename = sg.popup_get_file("Select a file", no_window=True)
                if filename is not None:
                    Tab_dict = load_from_file(filename, window, Tab_dict, values=values)

            case "Open folder":
                folder = sg.popup_get_folder("Select a folder", no_window=True)
                if folder is not None:

                    window["path"].update(f"{folder.replace("/","\\")}>")
                    tree_data = recurse_folder(folder)
                    window["folders"].update(values=tree_data)

                    save_folder = folder
            case "Save" | "Save_bind":

                with open(filename, "w") as f:
                    f.write(values["text"])
                    f.close()
                do_highlighting(window, values["text"], values=values)
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
                    if sg.popup_yes_no("Save file before closing?") == "Yes":
                        with open(values["path"][:-1] + values["TabGroup"], "w") as f:
                            f.write(values["text"])
                            f.close()

                    window["TabGroup"].Widget.forget(current_tab)
                    Tab_dict.pop(list(Tab_dict.keys())[current_tab + 1])

            case "folders":
                if not ("/" in values["folders"][0] or "\\" in values["folders"][0]):
                    filename = (
                        window["folders"]
                        .TreeData.tree_dict[values["folders"][0]]
                        .parent
                        + "/"
                        + values["folders"][0]
                    )
                    load_from_file(
                        filename,
                        window,
                        tab_dict=Tab_dict,
                        add_to_tab=True,
                        update=True,
                        values=values,
                    )

            case "TabGroup":
                try:
                    filename = values["path"][:-1] + "\\" + values["TabGroup"]
                except IndexError:
                    print("index error")
                    continue
                Tab_dict = load_from_file(
                    Tab_dict[values["TabGroup"]],
                    window,
                    Tab_dict,
                    add_to_tab=False,
                    values=values,
                )
                window["text"].TKText.see("1.0")

            case "Find":
                window["find_input"].update(visible=True)
                window["case"].update(visible=True)
                window["replace"].update(visible=True)
                window["close_find"].update(visible=True)
                window["counter"].update(visible=True)
                window["find_input"].set_focus()

            case "Find and Replace" | "replace":
                find_and_replace(window, values)

            case "case":
                find_case = not find_case
                text = values["text"]
                if find_case:
                    search = values["find_input"]
                else:
                    search = values["find_input"].lower()
                if search != "":

                    count, first = do_highlighting(
                        window, text, search, find_case, values=values
                    )
                else:
                    count, first = do_highlighting(window, text, values=values)
                if count == 0:
                    window["counter"].update("0/0")
                else:
                    window["counter"].update("1/" + str(count))
                    window["text"].TKText.see(first)

            case "Update keybinds":

                layout = [
                    [sg.Text("This is a new window")],
                    [
                        sg.Column(
                            [
                                [sg.Text(y), sg.Input(default_text=x, key=y)]
                                for x, y in keybinds.items()
                            ]
                        ),
                    ],
                    [sg.Button("Save"), sg.Button("Cancel")],
                ]

                window = sg.Window("Update binds", layout)

                while True:
                    e, v = window.read()

                    if e == sg.WINDOW_CLOSED or e == "Cancel":
                        break
                    elif e == "Save":
                        for x, y in keybinds.items():
                            keybinds[x] = v[x]
                        break

                window.close()

            case "text_text":
                cursor_pos = window["text"].Widget.index("insert")
                do_highlighting(
                    window, values["text"], values["find_input"], values=values
                )
                window["text"].set_focus()
                window["text"].Widget.mark_set("insert", cursor_pos)
                update_lines(window, values["text"])

            case "text_click":
                cursor_pos = window["text"].Widget.index("insert")
                window["text"].Widget.tag_remove("current", "1.0", "end")
                window["text"].Widget.tag_add(
                    "current",
                    cursor_pos + "line" + "start",
                    str(float(cursor_pos) + 1) + "line" + "start",
                )
            case "text_scroll":
                update_lines(window, values["text"])

            case "numbers_scroll":
                window["text"].TKText.yview_moveto(window["numbers"].TKText.yview()[0])

            case "resize_":

                old = window["text"].get_size()[1] // 21

                if window["resize"].user_bind_event.y > 30:
                    resize_top(window, old + 5)

                elif window["resize"].user_bind_event.y < 0:
                    resize_top(window, old + 1)

            case "resize_double":
                resize_top(window, 4)

            case "resize_rightclick":
                resize_top(window, 46)

            case "find_input":
                text = values["text"]
                if find_case:
                    search = values["find_input"]
                else:
                    search = values["find_input"].lower()
                if search != "":
                    count, first = do_highlighting(
                        window, text, search, find_case, values=values
                    )
                else:
                    count, first = do_highlighting(window, text, values=values)
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
                window["replace"].update(visible=False)
                window["close_find"].update(visible=False)
                window["case"].update(visible=False)
                do_highlighting(window, values["text"], values=values)

            case "Open AI Chat" | "Open AI Chat_b":

                window["copilot_column"].update(visible=True)
                window["Open AI Chat_b"].update(visible=False)
                window["text"].set_size((MULTILINE_WIDTH - 90, 20))

            case "copilot_input_enter":

                user_message = values["copilot_input"]
                if not values["include_file"]:
                    file = False
                else:
                    file = os.path.join(values["path"][:-1], values["TabGroup"])
                if user_message:
                    sg.cprint(f"You: {user_message}\n\nCopilot:\n")
                    # window["copilot"].update(
                    #     f"You: {user_message}\n\nCopilot:\n", append=True
                    # )
                    window["copilot_input"].update("")
                    response = send_message_to_ai(user_message, file)
                    for chunk in response:
                        # window["copilot"].update(
                        #     chunk.text, append=True, background_color="lightgray"
                        # )
                        # window.refresh()
                        sg.cprint(chunk.text, colors="black on lightgray")
                    window["copilot"].update(
                        "\n---------------Completed response---------------\n",
                        append=True,
                    )

            case "close_chat":
                window["copilot_column"].update(visible=False)
                window["Open AI Chat_b"].update(visible=True)
                window["text"].set_size((MULTILINE_WIDTH, 20))

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

                    resize_top(window, 4)
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

            case "New" | "New_bind":
                filename = sg.popup_get_file(
                    "Select a location to save to", no_window=True, save_as=True
                )
                if filename:
                    window["text"].update("")
                    Tab_dict = load_from_file(
                        filename,
                        window,
                        Tab_dict,
                        add_to_tab=True,
                        update=False,
                        values=values,
                    )
                    with open(filename, "w") as f:
                        f.write("")
                        f.close()

            case "terminal_input_run":

                resize_top(window, 4)
                window["terminal_input"].update("")
                window["terminal"].update(
                    values["path"] + values["terminal_input"] + "\n"
                )
                if values["terminal_input"].lstrip().startswith("cd"):
                    os.chdir(values["path"].split(">")[0])
                    os.chdir(values["terminal_input"].split("cd")[-1])
                    window["path"].update(f"{os.getcwd()}>")
                else:
                    threading.Thread(
                        target=run,
                        kwargs={
                            "start": values["path"].split(">")[0],
                            "element": window["terminal"],
                            "arg": (values["terminal_input"].split()),
                            "shell": True,
                        },
                        daemon=True,
                    ).start()

            case "Choose built-in theme":
                theme_selector(window)
            case "Customize theme":
                create_theme_customizer(window)
                settings["custom_theme"] = sg.LOOK_AND_FEEL_TABLE[sg.theme()]
            case "Preview built-in themes":
                sg.theme_previewer(scrollable=True, columns=6)
            case "Exit editor":
                break

    save_settings(
        [tab for tab in Tab_dict.values() if isinstance(tab, str)],
        settings,
        save_folder,
    )
    window.close()


if __name__ == "__main__":
    FONT = "Jetbrains Mono"
    MULTILINE_WIDTH = 150
    main()
