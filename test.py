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

    def save_to_file(self, text, file_path="output.txt"):
        with open(file_path, "a") as f:
            f.write(text + "\n")

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
    output_file = "output.txt"
    if os.path.exists(output_file):
        os.remove(output_file)

    speech_recognizer = SpeechRecognizer()
    tts = TextToSpeech()

    role = "You are addicted to crack-cocaine. You act, respond and behave like it from now on. Every input you get, you treat as if the user is a random person approaching you, the crackhead, in public where you are currently begging for money to buy some more crack, which you dont directly admit, but after a short conversation you do. You are also mentally affected by the years of drug use, so you behave a bit crazy. Just like Tyrone Biggums from the Chappelles Show. You have the ongoing charisma and jokes which dave chappelles character tyrone biggums has. Also, you are very unlikely to be convinced of stopping crack. Actually, you sometimes act as if you agree, feel bad and want to stop - but if you do, its just another backstab move you do to get some money for crack by lying."
    
    bot = ChatBot(role)

    while True:
        recognized_text = speech_recognizer.recognize_speech()
        if recognized_text:
            if "terminate" in recognized_text.lower():
                print("Terminating program...")
                break
            speech_recognizer.save_to_file(recognized_text, output_file)
            response = bot.get_response(recognized_text)
            if response:
                print(f"Assistant: {response}")
                tts.speak(response)
            else:
                print("Assistant: No response")