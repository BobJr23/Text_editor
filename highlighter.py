import re
import PySimpleGUI as sg
import time
import tkinter as tk


# I Used ChatGPT for creating these regex patterns
pattern_py = {
    "comment": r"(#.*?$)",
    "string": r"(\".*?\"|\'.*?\')",
    "parentheses": r"[()\[\]{}]",
    "function": r"([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\()",
    "numbers": r"[-+]?\b\d+(?:\.\d*)?(?:[eE][-+]?\d+)?\b",
    "keyword": r"\b(and|as|assert|break|class|continue|def|del|elif|else|except|False|finally|for|from|global|if|import|in|is|lambda|move|nonlocal|not|or|pass|raise|return|True|try|with|while|yield)\b",
}

pattern_go = {
    "comment": r"(\/\/.*?$|\/\*.*?\*\/)",
    "string": r"\"(\\.|[^\"])*\"|`([^`]|\\`)*`",
    "parentheses": r"[()\[\]{}]",
    "function": r"\b(func)\s+([a-zA-Z_][a-zA-Z0-9_]*)\b",
    "numbers": r"[-+]?\b\d+(?:\.\d*)?(?:[eE][-+]?\d+)?\b",
    "keyword": r"\b(break|default|func|interface|select|case|defer|go|map|struct|chan|else|goto|package|switch|const|fallthrough|if|range|type|continue|for|import|return|var)\b",
}

pattern_java = {
    "comment": r"(\/\/.*?$|\/\*.*?\*\/)",
    "string": r"\"(\\.|[^\"])*\"",
    "parentheses": r"[()\[\]{}]",
    "function": r"\b([a-zA-Z_][a-zA-Z0-9_]*)\s*(?=\()",
    "numbers": r"[-+]?\b\d+(?:\.\d*)?(?:[eE][-+]?\d+)?\b",
    "keyword": r"\b(abstract|assert|boolean|break|byte|case|catch|char|class|const|continue|default|do|double|else|enum|extends|final|finally|float|for|goto|if|implements|import|instanceof|int|interface|long|native|new|null|package|private|protected|public|return|short|static|strictfp|super|switch|synchronized|this|throw|throws|transient|try|void|volatile|while)\b",
}


pattern_dict = {"py": pattern_py, "go": pattern_go, "java": pattern_java}

styles = {
    # One dark Pro theme (best theme) obtained from screenshotting :D
    "keyword": {"text_color": "#c678dd"},
    "string": {"text_color": "#98c379"},
    "comment": {"text_color": "#5c6370"},
    "parentheses": {"text_color": "#e8ba36"},
    "function": {"text_color": "#61afef"},
    "numbers": {"text_color": "#c7935f"},
    "normal": {"text_color": "#a3b1be"},
}


def highlight_code(text, find="", find_case=False, patterns=None):
    segments = []
    if find != "":
        if find_case:
            comp = re.compile(re.escape(find), re.MULTILINE)
            print(find)
            print("ignoring")
            print(text)
        else:
            comp = re.compile(re.escape(find), re.MULTILINE | re.IGNORECASE)

        for match in comp.finditer(text):
            start, end = match.span()
            segments.append(("find", start, end))
        print(segments)
    if not patterns:
        return segments
    combined_pattern = "|".join(
        f"(?P<{name}>{pattern})" for name, pattern in patterns.items()
    )
    compiled_pattern = re.compile(combined_pattern, re.MULTILINE)

    for match in compiled_pattern.finditer(text):
        start, end = match.span()
        pattern_name = next(name for name, value in match.groupdict().items() if value)

        segments.append(
            (
                pattern_name,
                start,
                end,
            )
        )

    return segments


def do_highlighting(
    window: sg.Window, input_text, find="", find_case=False, values=None
):

    try:
        extension = values["TabGroup"].split(".")[-1]
    except AttributeError:
        extension = None
    if extension in pattern_dict:
        current_pattern = pattern_dict[extension]
    else:
        current_pattern = None
    highlighted_segments = highlight_code(
        input_text, find, find_case, patterns=current_pattern
    )

    text_widget = window["text"].Widget
    text_widget.delete("1.0", tk.END)
    text_widget.insert("1.0", input_text[:-1])

    text_widget.tag_add("normal", "1.0", tk.END)
    first = None
    for pattern_name, start, end in highlighted_segments:
        start_idx = f"1.0 + {start}c"
        end_idx = f"1.0 + {end}c"
        text_widget.tag_add(pattern_name, start_idx, end_idx)
        if pattern_name == "find" and first is None:
            first = start_idx
    if find_case:
        return input_text.count(find) if find != "" else 0, first
    return input_text.lower().count(find.lower()) if find != "" else 0, first


if __name__ == "__main__":
    p = highlight_code(
        r"import time\n\nfor x in range(30):\n    print(x)\n    time.sleep(0.05)",
        find="Tim",
        find_case=True,
    )
    print(p)
