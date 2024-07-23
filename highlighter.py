import re
import PySimpleGUI as sg

patterns = {
    "string": r"(\".*?\"|\'.*?\')",
    "comment": r"(#.*?$)",
}

styles = {
    "string": {"text_color": "green"},
    "comment": {"text_color": "grey"},
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


def do_highlighting(window, input_text):

    highlighted_segments = highlight_code(input_text)
    window["text"].update("")
    for segment in highlighted_segments:

        pattern_name, text_segment = segment
        if pattern_name == "normal":
            window["text"].print(text_segment, text_color="darkgrey", end="")
        else:
            style = styles[pattern_name]
            window["text"].print(text_segment, text_color=style["text_color"], end="")
