import dotenv
import os
import PySimpleGUI as sg
import google.generativeai as genai

dotenv.load_dotenv()

genai.configure(api_key=os.getenv("API_KEY"))

model = genai.GenerativeModel("gemini-1.5-flash")


def send_message_to_ai(message, file):
    if file:
        current_file = genai.upload_file(file)
        result = model.generate_content([current_file, "\n\n", message], stream=True)
    else:
        result = model.generate_content([message], stream=True)
    return result


def open_chat_window(file):
    layout = [
        [sg.Multiline(size=(200, 50), key="-CHAT-", disabled=True, autoscroll=True)],
        [
            sg.Input(key="-INPUT-", size=(40, 1)),
            sg.Button("Send", bind_return_key=True),
            sg.Checkbox("Include File", key="-INCLUDE_FILE-"),
        ],
    ]

    window = sg.Window("AI Chat", layout, finalize=True)

    chat_history = ""

    while True:
        event, values = window.read()
        if event == sg.WINDOW_CLOSED:
            break
        elif event == "Send":
            user_message = values["-INPUT-"]
            if not values["-INCLUDE_FILE-"]:
                file = False
            if user_message:
                window["-CHAT-"].update(f"You: {user_message}\n", append=True)
                window["-INPUT-"].update("")
                response = send_message_to_ai(user_message, file)
                for chunk in response:
                    window["-CHAT-"].update(chunk.text, append=True)
                    window.refresh()
                window["-CHAT-"].update("\n___________________\n", append=True)

    window.close()


if __name__ == "__main__":
    open_chat_window(__file__)
