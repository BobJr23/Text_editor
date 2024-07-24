import re
import PySimpleGUI as sg
import tkinter as tk

# Define regex patterns for Python syntax
patterns = {
    "keyword": r"\b(import|from|as|if|else|elif|for|while|def|return|in|and|or|not|is|class|try|except|finally|with|lambda|yield|assert|break|continue|del|global|nonlocal|pass|raise|True|False|None)\b",
    "string": r"(\".*?\"|\'.*?\')",
    "comment": r"(#.*?$)",
    "function": r"([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\()",
    "test": r"test",
}

# Combine patterns into a single regex with named groups
combined_pattern = "|".join(
    f"(?P<{name}>{pattern})" for name, pattern in patterns.items()
)
compiled_pattern = re.compile(combined_pattern, re.MULTILINE)

# Define styles
styles = {
    "keyword": {"text_color": "blue"},
    "string": {"text_color": "green"},
    "comment": {"text_color": "grey"},
    "function": {"text_color": "purple"},
    "test": {"text_color": "red"},
    "normal": {"text_color": "black"},
}


# Define the highlight function
def highlight_code(text):
    segments = []
    last_end = 0
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
    return segments


# Create the PySimpleGUI layout
layout = [
    [sg.Text("Enter Python Code:")],
    [sg.Multiline(size=(80, 20), key="-INPUT-")],
    [sg.Button("Highlight")],
    [sg.Text("Highlighted Code:")],
    [
        sg.Multiline(
            size=(80, 20), key="-OUTPUT-", disabled=True, background_color="white"
        )
    ],
]

window = sg.Window("Syntax Highlighter", layout)

# Event loop
while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED:
        break
    if event == "Highlight":
        input_text = values["-INPUT-"]
        highlighted_segments = highlight_code(input_text)

        # Build the complete output string
        output_text = ""
        for segment in highlighted_segments:
            pattern_name, text_segment = segment
            style = styles[pattern_name]
            output_text += text_segment

        # Update the output field once
        window["-OUTPUT-"].update(output_text)

        # Access the underlying Tkinter Text widget to apply tag-based styling
        text_widget = window["-OUTPUT-"].Widget
        text_widget.delete("1.0", tk.END)
        text_widget.insert("1.0", output_text)

        for segment in highlighted_segments:
            pattern_name, text_segment = segment
            style = styles[pattern_name]
            start_idx = text_widget.search(text_segment, "1.0", tk.END)
            end_idx = f"{start_idx}+{len(text_segment)}c"
            text_widget.tag_add(pattern_name, start_idx, end_idx)
            text_widget.tag_config(pattern_name, foreground=style["text_color"])

window.close()
