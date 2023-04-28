import os
import json
import openai
import pygame
import threading
import tkinter as tk
from io import BytesIO
from tkinter import messagebox
import speech_recognition as sr
from elevenlabs import generate,play, set_api_key, voices

openai.api_key = "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"
set_api_key("c2eec6c0f165617aa2c3e87f06c6bc10")


class SpeechRecognizer:
    def __init__(self, is_conversing_event):
        self.recognizer = sr.Recognizer()
        self.is_conversing_event = is_conversing_event

    def recognize_speech(self):
        if not self.is_conversing_event.is_set():
            return None

        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            if not self.is_conversing_event.is_set():
                return None
            audio = self.recognizer.listen(source)

        if not self.is_conversing_event.is_set():
            return None

        try:
            print("Recognizing...")
            text = self.recognizer.recognize_google(audio)
            os.system("cls")
            return text
        except sr.UnknownValueError:
            print("Could not understand audio. Please try again.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None


class TextToSpeech:
    def __init__(self, voice, language="en", slow=False):
        self.language = language
        self.slow = slow
        self.voice = voice
        pygame.mixer.init()

    def play(self, audio: bytes, notebook: bool = False) -> None:
        if notebook:
            from IPython.display import Audio, display
            display(Audio(audio, rate=44100, autoplay=True))
        else:
            pygame.mixer.music.load(BytesIO(audio))
            pygame.mixer.music.play()

    def speak(self, text):
        audio = generate(text=text, voice=self.voice)
        self.play(audio)

    def stop(self):
        pygame.mixer.music.stop()


class ChatBot:
    def __init__(self, role):
        self.role = role
        self.messages = [{"role": "system", "content": self.role}]

    def add_message(self, role, content):
        self.messages.append({"role": role, "content": content})

    def get_response(self, user_input):
        self.add_message("user", user_input)
        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo", messages=self.messages)
        except Exception as e:
            print(
                f"Error occurred while getting response from OpenAI API: {e}")
            return None

        result = response.choices[0].message.content
        self.add_message("assistant", result)
        return result


class ChatbotApp(tk.Tk):
    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.is_conversing = False
        self.title("Chatbot")
        self.geometry("800x600")
        self.configure(bg="#2c2c2c")
        self.is_conversing_event = threading.Event()
        # Main frame
        self.main_frame = tk.Frame(self, bg="#2c2c2c")
        self.main_frame.pack(padx=10, pady=10, fill="both", expand=True)
        # Video frame
        self.video_frame = tk.Frame(self.main_frame)
        self.video_frame.pack(fill="both", expand=True)
        # Your camera output
        self.your_camera = tk.Label(
            self.video_frame, text="Your Camera Output", bg="#4a4a4a", fg="white", width=40, height=20)
        self.your_camera.pack(side="left", padx=(
            0, 5), pady=(0, 5), fill="both", expand=True)
        # AI's video output
        self.ai_camera = tk.Label(
            self.video_frame, text="AI's Video Output", bg="#4a4a4a", fg="white", width=40, height=20)
        self.ai_camera.pack(side="right", padx=(
            5, 0), pady=(0, 5), fill="both", expand=True)
        # Bottom frame
        self.bottom_frame = tk.Frame(self, bg="#3c3c3c")
        self.bottom_frame.pack(padx=1, pady=1, fill="x")
        # Choose role drop-down menu
        self.choose_role_var = tk.StringVar()
        self.choose_role_var.set("Choose Role")
        self.choose_role_menu = tk.OptionMenu(
            self.bottom_frame, self.choose_role_var, *roles_data.keys(), command=self.set_role,)
        self.choose_role_menu.grid(row=0, column=0, padx=(0, 10))
        self.choose_role_menu.config(width=14, bg="#4a4a4a", fg="white")
        # Chat history
        self.chat_history = tk.Text(self.bottom_frame, wrap="word", height=6, state="disabled", font=(
            "Courier", 10), bg="#3c3c3c", fg="white")
        self.chat_history.grid(row=0, column=1, padx=(0, 10), sticky="ew")
        self.bottom_frame.columnconfigure(1, weight=2)
        # start
        self.start_conversation_button = tk.Button(
            self.bottom_frame, text="Start Conversation", command=self.start_conversation, width=14, bg="#4a4a4a", fg="white")
        self.start_conversation_button.grid(row=0, column=3)

    def set_role(self, role_name):
        global bot_name, role, bot, voice_role, tts
        bot_name = role_name
        role = roles_data[bot_name]
        bot = ChatBot(role)
        voice_role = voices_map[bot_name]
        tts = TextToSpeech(voice=voice_role)
        self.choose_role_var.set(f"Role: {bot_name}")

    def start_conversation(self):
        self.is_conversing_event.set()
        self.start_conversation_button.config(
            text="End Conversation", command=self.end_conversation)
        conversation_thread = threading.Thread(target=self.conversation_loop)
        conversation_thread.start()

    def end_conversation(self):
        self.is_conversing_event.clear()
        self.start_conversation_button.config(
            text="Start Conversation", command=self.start_conversation)
        tts.stop()
        self.chat_history.configure(state="normal")
        self.chat_history.delete(1.0, tk.END)
        self.chat_history.configure(state="disabled")
        bot.messages = [{"role": "system", "content": bot.role}]

    def conversation_loop(self):
        recognizer = SpeechRecognizer(self.is_conversing_event)
        while self.is_conversing_event.is_set():
            user_input = recognizer.recognize_speech()
            if user_input is not None and self.is_conversing_event.is_set():
                if "terminate" in user_input.lower():
                    if messagebox.askyesno("Termination", "Do you want to terminate the program?"):
                        self.quit()
                else:
                    response = bot.get_response(user_input)
                    if response:
                        self.chat_history.configure(state="normal")
                        self.chat_history.insert(
                            tk.END, f"You: {user_input}\n")
                        self.chat_history.insert(
                            tk.END, f"{bot_name}: {response}\n")
                        self.chat_history.configure(state="disabled")
                        self.chat_history.see(tk.END)
                        tts.speak(response)


if __name__ == "__main__":
    voices("c2eec6c0f165617aa2c3e87f06c6bc10")
    script_path = os.path.dirname(os.path.realpath(__file__))
    roles_file = os.path.join(script_path, 'roles.json')
    with open(roles_file, 'r') as file:
        roles_data = json.load(file)
    voices_map = {
        "crackhead": "crackhead",
        "employee-kaufland": "Domi",
        "Markus": "Markus",
        "crusader": "Antoni",
        "mike-tyson": "Adam",
        "batman": "Domi",
        "batman-rogue": "Antoni",
        "eminem": "Adam"
    }
    app = ChatbotApp()
    app.mainloop()
