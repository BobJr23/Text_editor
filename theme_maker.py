import PySimpleGUI as sg


def rgb_to_hex(r, g, b):
    return "#{:02x}{:02x}{:02x}".format(r, g, b)


def hex_to_rgb(color):
    if isinstance(color, tuple):
        return color if len(color) == 3 else (color[0], color[0], color[0])
    elif isinstance(color, str):
        return tuple(int(color.lstrip("#")[i : i + 2], 16) for i in (0, 2, 4))
    else:
        return (color, color, color)


def create_color_sliders(key_prefix, text):
    return [
        [sg.Text(text)],
        [
            sg.Slider(
                range=(0, 255), orientation="h", size=(20, 15), key=f"-{key_prefix}_R-"
            ),
            sg.Slider(
                range=(0, 255), orientation="h", size=(20, 15), key=f"-{key_prefix}_G-"
            ),
            sg.Slider(
                range=(0, 255), orientation="h", size=(20, 15), key=f"-{key_prefix}_B-"
            ),
        ],
    ]


def get_color_from_sliders(values, key_prefix):
    return rgb_to_hex(
        int(values[f"-{key_prefix}_R-"]),
        int(values[f"-{key_prefix}_G-"]),
        int(values[f"-{key_prefix}_B-"]),
    )


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
        [
            sg.Text(
                "              RED                                         GREEN                                        BLUE"
            )
        ],
        *create_color_sliders("BG", "Background Color"),
        *create_color_sliders("TEXT", "Text Color"),
        *create_color_sliders("INPUT", "Input Background Color"),
        *create_color_sliders("INPUT_TEXT", "Input Text Color"),
        *create_color_sliders("BUTTON", "Button Color"),
        *create_color_sliders("BUTTON_TEXT", "Button Text Color"),
        *create_color_sliders("CURSOR", "Cursor Color"),
        *create_color_sliders("HIGHLIGHT", "Highlight Color"),
        [sg.Text("Preview")],
        [
            sg.Multiline(
                "This is a preview of the custom theme.\nYou can see how it looks here.",
                size=(50, 5),
                key="-PREVIEW-",
            )
        ],
        [sg.Input("Input field preview", key="-PREVIEW_INPUT-")],
        [sg.Button("Preview Button", key="-PREVIEW_BUTTON-")],
        [sg.Button("Apply"), sg.Button("Cancel")],
    ]

    window = sg.Window("Theme Customizer", layout, finalize=True)

    # Set initial slider values based on current theme
    color_mappings = {
        "BG": "BACKGROUND",
        "TEXT": "TEXT",
        "INPUT": "INPUT",
        "INPUT_TEXT": "TEXT_INPUT",
        "BUTTON": ("BUTTON", 1),  # Button background
        "BUTTON_TEXT": ("BUTTON", 0),  # Button text
        "CURSOR": "TEXT",  # Default to text color
        "HIGHLIGHT": "BUTTON",  # Default to button background
    }

    for key, theme_key in color_mappings.items():
        if isinstance(theme_key, tuple):
            color = hex_to_rgb(current_theme[theme_key[0]][theme_key[1]])
        else:
            color = hex_to_rgb(current_theme.get(theme_key, "#000000"))
        window[f"-{key}_R-"].update(color[0])
        window[f"-{key}_G-"].update(color[1])
        window[f"-{key}_B-"].update(color[2])
    while True:
        event, values = window.read(timeout=100)

        if event in (sg.WINDOW_CLOSED, "Cancel"):
            break

        if event == "Apply":
            new_theme = {
                "BACKGROUND": get_color_from_sliders(values, "BG"),
                "TEXT": get_color_from_sliders(values, "TEXT"),
                "INPUT": get_color_from_sliders(values, "INPUT"),
                "TEXT_INPUT": get_color_from_sliders(values, "INPUT_TEXT"),
                "BUTTON": (
                    get_color_from_sliders(values, "BUTTON_TEXT"),
                    get_color_from_sliders(values, "BUTTON"),
                ),
            }
            sg.LOOK_AND_FEEL_TABLE["CustomTheme"] = new_theme
            sg.theme("CustomTheme")
            sg.popup("Theme applied successfully!")

        bg_color = get_color_from_sliders(values, "BG")
        input_bg_color = get_color_from_sliders(values, "INPUT")
        input_text_color = get_color_from_sliders(values, "INPUT_TEXT")

        window["-PREVIEW-"].update(
            background_color=input_bg_color, text_color=input_text_color
        )

        window["-PREVIEW_INPUT-"].update(
            background_color=input_bg_color, text_color=input_text_color
        )

        window.TKroot.config(background=bg_color)
    window.close()
    return window


if __name__ == "__main__":
    # theme_selector(sg.Window("Theme Selector", layout=[]).Finalize())
    create_theme_customizer()
    print(sg.theme_background_color())
    print(sg.theme_text_color())
    print(sg.theme_button_color())
    print(sg.theme_input_background_color())
    # theme_selector()
