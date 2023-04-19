import os
import json
import openai
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play

import os
import openai
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
from pydub import AudioSegment
from pydub.playback import play

openai.api_key = "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"

class SpeechRecognizer:
    """A class to recognize speech from microphone input."""

    def __init__(self):
        self.recognizer = sr.Recognizer()

    def recognize_speech(self):
        """Listen to the microphone and return the recognized text."""
        with sr.Microphone() as source:
            print("Listening...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)
        try:
            print("Recognizing...")
            text = self.recognizer.recognize_google(audio)
            return text
        except sr.UnknownValueError:
            print("Could not understand audio. Please try again.")
            return None
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
            return None

class TextToSpeech:
    def __init__(self, language="en", slow=False):
        self.language = language
        self.slow = slow

    def speak(self, text):
        """Speak the given text."""
        speech = gTTS(text=text, lang=self.language, slow=self.slow)
        audio_bytes = BytesIO()
        speech.write_to_fp(audio_bytes)
        audio_bytes.seek(0)
        audio_segment = AudioSegment.from_file(audio_bytes, format="mp3")
        play(audio_segment)

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
                model="gpt-3.5-turbo",
                messages=self.messages
            )
        except Exception as e:
            print(f"Error occurred while getting response from OpenAI API: {e}")
            return None

        result = response.choices[0].message.content
        self.add_message("assistant", result)
        return result


if __name__ == "__main__":
    speech_recognizer = SpeechRecognizer()
    tts = TextToSpeech()

    script_path = os.path.dirname(os.path.realpath(__file__)) # path of this script
    roles_file  = os.path.join(script_path, 'roles.json') # path of the json file, containing the roles
    with open(roles_file, 'r') as file:
        roles_data = json.load(file) # roles_data is now a dictionary

    print("Available roles:")
    for role in roles_data:
        print(role)

    while True:
        bot_name = input("Enter role for bot: ")
        if bot_name in roles_data:
            role = roles_data[bot_name]
            bot = ChatBot(role)
            break
        else:
            print("Invalid role. Please try again.")


    while True:
        recognized_text = speech_recognizer.recognize_speech()
        if recognized_text:
            if "terminate" in recognized_text.lower():
                print("Terminating program...")
                break
            response = bot.get_response(recognized_text)
            if response:
                print(f"{bot_name}: {response}")
                tts.speak(response)
            else:
                print(f"{bot_name}: No response")
