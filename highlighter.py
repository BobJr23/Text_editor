import re
import PySimpleGUI as sg
import time
import tkinter as tk

# I Used ChatGPT for creating these regex patterns
patterns = {
    "comment": r"(#.*?$)",
    "string": r"(\".*?\"|\'.*?\')",
    "function": r"([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\()",
    "keyword": r"\b(and|as|assert|break|class|continue|def|del|elif|else|except|False|finally|for|from|global|if|import|in|is|lambda|move|nonlocal|not|or|pass|raise|return|True|try|with|while|yield)\b",
}

styles = {
    # One dark Pro theme (best theme) obtained from screenshotting :D
    "keyword": {"text_color": "#c678dd"},
    "string": {"text_color": "#98c379"},
    "comment": {"text_color": "#5c6370"},
    "function": {"text_color": "#61afef"},
    "normal": {"text_color": "#a3b1be"},
}


def highlight_code(text, find=""):
    segments = []
    if find != "":

        comp = re.compile(re.escape(find), re.MULTILINE | re.IGNORECASE)

        for match in comp.finditer(text):
            start, end = match.span()
            segments.append(("find", start, end, match.group()))

    combined_pattern = "|".join(
        f"(?P<{name}>{pattern})" for name, pattern in patterns.items()
    )
    compiled_pattern = re.compile(combined_pattern, re.MULTILINE)

    for match in compiled_pattern.finditer(text):
        start, end = match.span()
        pattern_name = next(name for name, value in match.groupdict().items() if value)
        segments.append((pattern_name, start, end, match.group()))

    return segments


def do_highlighting(window: sg.Window, input_text, find=""):
    highlighted_segments = highlight_code(input_text, find)
    t = time.time()
    window["text"].update("")

    text_widget = window["text"].Widget
    text_widget.delete("1.0", tk.END)
    text_widget.insert("1.0", input_text)

    for pattern_name in styles:
        text_widget.tag_config(
            pattern_name, foreground=styles[pattern_name]["text_color"]
        )
    text_widget.tag_config("find", background="orange", foreground="white")
    first = None
    print(highlighted_segments)
    for pattern_name, start, end, _ in highlighted_segments:
        start_idx = f"1.0 + {start}c"
        end_idx = f"1.0 + {end}c"
        text_widget.tag_add(pattern_name, start_idx, end_idx)
        if pattern_name == "find" and first is None:
            first = start_idx

    return input_text.count(find), first


highlight_code(
    r"import time\n\nfor x in range(30):\n    print(x)\n    time.sleep(0.05)"
)
