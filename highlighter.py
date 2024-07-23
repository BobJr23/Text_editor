import re
import PySimpleGUI as sg

# I Used ChatGPT for creating these regex patterns
patterns = {
    "keyword": r"\b(import|from|as|if|else|elif|for|while|def|return|in|and|or|not|is|class|try|except|finally|with|lambda|yield|assert|break|continue|del|global|nonlocal|pass|raise|True|False|None)\b",
    "string": r"(\".*?\"|\'.*?\')",
    "comment": r"(#.*?$)",
    "function": r"([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\()",
}

styles = {
    # One dark Pro theme (best theme) obtained from screenshotting :D
    "keyword": {"text_color": "#c678dd"},
    "string": {"text_color": "#98c379"},
    "comment": {"text_color": "#5c6370"},
    "function": {"text_color": "#61afef"},
}


def highlight_code(text):
    segments = []
    index = 0
    while index < len(text):
        matches = [
            (pattern_name, match.start(), match.end())
            for pattern_name, pattern in patterns.items()
            for match in re.finditer(pattern, text[index:], re.MULTILINE)
        ]
        if not matches:
            segments.append(("normal", text[index:]))
            break

        earliest_match = min(matches, key=lambda x: x[1])
        pattern_name, start, end = earliest_match
        start += index
        end += index

        if start > index:
            segments.append(("normal", text[index:start]))

        segments.append((pattern_name, text[start:end]))
        index = end

    return segments


def do_highlighting(window: sg.Window, input_text):

    highlighted_segments = highlight_code(input_text)
    window["text"].update("")
    for segment in highlighted_segments:

        pattern_name, text_segment = segment

        if pattern_name == "normal":
            window["text"].print(text_segment, text_color="darkgrey", end="")
        else:
            style = styles[pattern_name]
            window["text"].print(text_segment, text_color=style["text_color"], end="")
