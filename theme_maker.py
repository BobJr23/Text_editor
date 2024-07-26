import PySimpleGUI as sg


def rgb_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


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


def theme_selector(window):
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


def create_theme_customizer():
    current_theme = sg.LOOK_AND_FEEL_TABLE[sg.theme()]

    layout = [
        [sg.Text("Background Color")],
        [
            sg.Slider(range=(0, 255), orientation="h", size=(20, 15), key="-BG_R-"),
            sg.Slider(range=(0, 255), orientation="h", size=(20, 15), key="-BG_G-"),
            sg.Slider(range=(0, 255), orientation="h", size=(20, 15), key="-BG_B-"),
        ],
        [sg.Text("Text Color")],
        [
            sg.Slider(range=(0, 255), orientation="h", size=(20, 15), key="-TEXT_R-"),
            sg.Slider(range=(0, 255), orientation="h", size=(20, 15), key="-TEXT_G-"),
            sg.Slider(range=(0, 255), orientation="h", size=(20, 15), key="-TEXT_B-"),
        ],
        [sg.Text("Highlight Color")],
        [
            sg.Slider(range=(0, 255), orientation="h", size=(20, 15), key="-HL_R-"),
            sg.Slider(range=(0, 255), orientation="h", size=(20, 15), key="-HL_G-"),
            sg.Slider(range=(0, 255), orientation="h", size=(20, 15), key="-HL_B-"),
        ],
        [sg.Text("Preview")],
        [
            sg.Multiline(
                "This is a preview of the custom theme.\nYou can see how it looks here.",
                size=(50, 5),
                key="-PREVIEW-",
            )
        ],
        [sg.Button("Apply"), sg.Button("Cancel")],
    ]

    window = sg.Window("Theme Customizer", layout, finalize=True)

    while True:
        event, values = window.read()

        if event in (sg.WINDOW_CLOSED, "Cancel"):
            break

        if event == "Apply":
            new_theme = {
                "BACKGROUND": rgb_to_hex(
                    int(values["-BG_R-"]), int(values["-BG_G-"]), int(values["-BG_B-"])
                ),
                "TEXT": rgb_to_hex(
                    int(values["-TEXT_R-"]),
                    int(values["-TEXT_G-"]),
                    int(values["-TEXT_B-"]),
                ),
                "BUTTON": (
                    rgb_to_hex(
                        int(values["-TEXT_R-"]),
                        int(values["-TEXT_G-"]),
                        int(values["-TEXT_B-"]),
                    ),
                    rgb_to_hex(
                        int(values["-HL_R-"]),
                        int(values["-HL_G-"]),
                        int(values["-HL_B-"]),
                    ),
                ),
            }
            sg.LOOK_AND_FEEL_TABLE["CustomTheme"] = new_theme
            sg.theme("CustomTheme")
            sg.popup("Theme applied successfully!")

        bg_color = rgb_to_hex(
            int(values["-BG_R-"]), int(values["-BG_G-"]), int(values["-BG_B-"])
        )
        text_color = rgb_to_hex(
            int(values["-TEXT_R-"]), int(values["-TEXT_G-"]), int(values["-TEXT_B-"])
        )
        highlight_color = rgb_to_hex(
            int(values["-HL_R-"]), int(values["-HL_G-"]), int(values["-HL_B-"])
        )

        window["-PREVIEW-"].update(
            background_color=bg_color,
            text_color=text_color,
        )


if __name__ == "__main__":
    create_theme_customizer()
    # theme_selector()
