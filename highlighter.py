import re
import PySimpleGUI as sg
import time
import tkinter as tk

# I Used ChatGPT for creating these regex patterns
patterns = {
    "function": r"([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\()",
    "string": r"(\".*?\"|\'.*?\')",
    "comment": r"(#.*?$)",
    "keyword": r"\b(and|as|assert|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|move|nonlocal|not|or|pass|raise|return|try|with|while|yield)\b",
}

styles = {
    # One dark Pro theme (best theme) obtained from screenshotting :D
    "keyword": {"text_color": "#c678dd"},
    "string": {"text_color": "#98c379"},
    "comment": {"text_color": "#5c6370"},
    "function": {"text_color": "#61afef"},
    "normal": {"text_color": "#a3b1be"},
}


def highlight_code(text, find=None):

    segments = []
    t = time.time()
    last_end = 0
    if find:
        new_patterns = {"find": find}
        new_patterns.update(patterns)
    else:
        new_patterns = patterns
    combined_pattern = "|".join(
        f"(?P<{name}>{pattern})" for name, pattern in new_patterns.items()
    )
    compiled_pattern = re.compile(combined_pattern, re.MULTILINE)

    for match in compiled_pattern.finditer(text):
        start, end = match.span()
        if start > last_end:
            segments.append(("normal", text[last_end:start]))
        for name, value in match.groupdict().items():
            if value:
                segments.append((name, value))
                break
        last_end = end
    if last_end < len(text):
        segments.append(("normal", text[last_end:]))
    print(time.time() - t)

    return segments


def do_highlighting(window: sg.Window, input_text, find=None):

    highlighted_segments = highlight_code(input_text, find)
    t = time.time()
    window["text"].update("")
    buffer = ""
    # METHOD 1
    # for segment in highlighted_segments:
    #
    #     pattern_name, text_segment = segment
    #
    #     if pattern_name == "find":
    #         window["text"].print(
    #             text_segment, text_color="white", background_color="orange", end=""
    #         )
    #     else:
    #         style = styles[pattern_name]
    #         # buffer += f'[{style["text_color"]}] {text_segment} '
    #         window["text"].print(text_segment, text_color=style["text_color"], end="")
    # METHOD 2 expereimental
    output_text = ""
    for segment in highlighted_segments:
        pattern_name, text_segment = segment
        style = styles[pattern_name]
        output_text += text_segment

    window["text"].update(output_text)

    text_widget = window["text"].Widget
    text_widget.delete("1.0", tk.END)
    text_widget.insert("1.0", output_text)

    for segment in highlighted_segments:
        pattern_name, text_segment = segment
        style = styles[pattern_name]
        start_idx = text_widget.search(text_segment, "1.0", tk.END)
        end_idx = f"{start_idx}+{len(text_segment)}c"
        text_widget.tag_add(pattern_name, start_idx, end_idx)
        text_widget.tag_config(pattern_name, foreground=style["text_color"])
    print(time.time() - t)


highlight_code(
    r"import time\n\nfor x in range(30):\n    print(x)\n    time.sleep(0.05)"
)
