import dotenv
import os
import PySimpleGUI as sg

dotenv.load_dotenv()

api_key = os.getenv("API_KEY")


def send_message_to_ai(message):
    return "response"


def open_chat_window():
    layout = [
        [sg.Multiline(size=(50, 20), key="-CHAT-", disabled=True, autoscroll=True)],
        [
            sg.Input(key="-INPUT-", size=(40, 1)),
            sg.Button("Send", bind_return_key=True),
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
            if user_message:
                chat_history += f"You: {user_message}\n"
                ai_response = send_message_to_ai(user_message)
                chat_history += f"AI: {ai_response}\n"
                window["-CHAT-"].update(chat_history)
                window["-INPUT-"].update("")

    window.close()


if __name__ == "__main__":
    open_chat_window()
