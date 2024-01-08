import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Embedding, LSTM, Dense
import speech_recognition as sr
import wikipedia
import pyttsx3
import threading
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedStyle

class SpeechRecognitionApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Speech Recognition App")

        # Set the window size and position it in the center of the screen
        screen_width = self.master.winfo_screenwidth()
        screen_height = self.master.winfo_screenheight()
        window_width = 800
        window_height = 500

        x_position = (screen_width - window_width) // 2
        y_position = (screen_height - window_height) // 2

        self.master.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Allow window resizing and add decorations
        self.master.resizable(True, True)
        self.master.attributes('-toolwindow', False)
        self.master.overrideredirect(False)

        # Use ThemedStyle for enhanced styling
        self.style = ThemedStyle(master)
        self.style.set_theme("equilux")  # Choose a theme (you can experiment with different themes)

        # UI elements
        self.create_ui()

        # Initialize the text-to-speech engine
        self.engine = pyttsx3.init()

        # Adjust the voice properties
        voices = self.engine.getProperty('voices')
        self.engine.setProperty('voice', voices[1].id)  # Use the voice of a female speaker

        # Set the speaking rate (adjust as needed)
        self.engine.setProperty('rate', 150)

        # Speech recognition setup
        self.recognizer = sr.Recognizer()
        self.is_recording = False
        self.is_talking = False  # Track whether the bot is currently talking

        # Initialize the RNN model for text input
        self.text_input_model = self.build_text_input_model()
        self.text_input_lock = threading.Lock()

    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.master, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Status labels, buttons, entry, etc.
        self.status_label = ttk.Label(main_frame, text="Status:")
        self.status_label.grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)

        self.status_indicator = ttk.Label(main_frame, text="", background="red", width=10)
        self.status_indicator.grid(row=0, column=1, padx=10, pady=5, sticky=tk.W)

        self.start_button = ttk.Button(main_frame, text="Start Recording", command=self.start_recording)
        self.start_button.grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)

        self.stop_button = ttk.Button(main_frame, text="Stop Recording", command=self.stop_recording, state=tk.DISABLED)
        self.stop_button.grid(row=1, column=1, padx=10, pady=5, sticky=tk.W)

        self.stop_talking_button = ttk.Button(main_frame, text="Stop Talking", command=self.stop_talking, state=tk.DISABLED)
        self.stop_talking_button.grid(row=1, column=2, padx=10, pady=5, sticky=tk.W)

        self.question_entry = ttk.Entry(main_frame, width=60)
        self.question_entry.grid(row=2, column=0, columnspan=3, padx=10, pady=5, sticky=tk.W)

        self.submit_button = ttk.Button(main_frame, text="Submit Question", command=self.submit_question)
        self.submit_button.grid(row=3, column=0, columnspan=3, padx=10, pady=5, sticky=tk.W)

        self.status_message_label = ttk.Label(main_frame, text="")
        self.status_message_label.grid(row=4, column=0, columnspan=3, padx=10, pady=5, sticky=tk.W)

        # Center the title
        ttk.Label(main_frame, text="Speech Recognition App", font=('Helvetica', 18, 'bold')).grid(row=5, column=0, columnspan=3, pady=10, sticky=tk.W)

        # Names in bold
        ttk.Label(main_frame, text="By Amal Malaak Bushra Raneem", font=('Helvetica', 10, 'bold')).grid(row=6, column=0, columnspan=3, pady=5, sticky=tk.W)

    def build_text_input_model(self):
        """
        Build and return the RNN model for text input.

        Explanation of the model:
        - Embedding Layer: Converts input text into dense vectors of fixed size (input_dim=10000, output_dim=16).
        - LSTM Layer: Long Short-Term Memory layer, a type of recurrent neural network layer.
          It helps capture long-term dependencies in the input sequence (units=32).
        - Dense Layer: Produces the final output, binary classification in this case (units=1, activation='sigmoid').

        Compile Configuration:
        - Optimizer: Adam optimizer, an adaptive learning rate optimization algorithm.
        - Loss: Binary crossentropy, suitable for binary classification tasks.
        - Metrics: Accuracy is used as the evaluation metric.

        Note: Modify the model architecture as needed for your specific task.
        """
        model = Sequential()

        # Embedding layer: Converts text data into dense vectors
        model.add(Embedding(input_dim=10000, output_dim=16, input_length=50))

        # LSTM layer: Captures long-term dependencies in the input sequence
        model.add(LSTM(units=32, return_sequences=True))  # return_sequences=True for stacked LSTM layers
        model.add(LSTM(units=32))  # Additional LSTM layer for more complex learning

        # Dense layer: Produces the final output
        model.add(Dense(units=1, activation='sigmoid'))

        # Model compilation
        model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
        return model

    def process_text_input(self, text):
        """
        Placeholder text processing; replace with your logic.
        This function currently converts text to uppercase.
        """
        return text.upper()

    def speak_intro(self):
        intro_text = "Hello! I am MAB.AI Bot. How can I assist you today?"
        self.engine.say(intro_text)
        self.engine.runAndWait()

    def start_recording(self):
        self.is_recording = True
        self.status_message_label.config(text="Waiting for your message...", foreground="black")
        self.status_indicator.config(text="Recording", background="green")
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.stop_talking_button.config(state=tk.NORMAL)  # Enable the "Stop Talking" button

        # Start a new thread for speech recognition
        threading.Thread(target=self.listen_and_process).start()

    def stop_recording(self):
        self.is_recording = False
        self.status_indicator.config(text="Stopped", background="red")
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.stop_talking_button.config(state=tk.DISABLED)  # Disable the "Stop Talking" button
        self.status_message_label.config(text="")

    def stop_talking(self):
        self.engine.stop()
        self.status_message_label.config(text="Bot speech stopped.", foreground="purple")

    def submit_question(self):
        question_text = self.question_entry.get()
        if question_text:
            processed_text = self.process_text_input(question_text)

            # Input data to Wikipedia search
            wikisearch = wikipedia.summary(processed_text)

            # Set the voice characteristics for the bot
            self.engine.setProperty('voice', self.engine.getProperty('voices')[1].id)  # Use the voice of a female speaker
            self.engine.setProperty('rate', 150)  # Adjust the speaking rate as needed

            # Speak the Wikipedia summary
            self.engine.say(wikisearch)
            self.engine.runAndWait()

    def listen_and_process(self):
        with sr.Microphone() as source:
            print('Clearing background noise... Please wait')
            self.recognizer.adjust_for_ambient_noise(source, duration=1)
            print("Waiting for your message...")

            try:
                self.speak_intro()  # Speak the bot's introduction
                while self.is_recording:
                    recorded_audio = self.recognizer.listen(source, timeout=5)
                    print('Done recording')

                    # Recognize speech using Google Speech Recognition
                    text = self.recognizer.recognize_google(recorded_audio, language='en-US')
                    print('Your Message:', format(text))

                    if "stop" in text.lower() or "pause" in text.lower():
                        self.status_message_label.config(text="Bot speech paused. You can resume by saying 'resume'", foreground="blue")
                        self.engine.stop()
                    elif "resume" in text.lower():
                        self.status_message_label.config(text="Bot speech resumed.", foreground="green")
                        self.speak_intro()
                    else:
                        # Process the text input using the RNN model
                        processed_text = self.process_text_input(text)

                        # Input data to Wikipedia search
                        wikisearch = wikipedia.summary(processed_text)

                        # Set the voice characteristics for the bot
                        self.engine.setProperty('voice', self.engine.getProperty('voices')[1].id)  # Use the voice of a female speaker
                        self.engine.setProperty('rate', 150)  # Adjust the speaking rate as needed

                        # Speak the Wikipedia summary
                        self.engine.say(wikisearch)
                        self.engine.runAndWait()

            except sr.UnknownValueError:
                print("MAB.AI Speech Recognition could not understand audio")
                self.status_message_label.config(text="Couldn't understand the audio. Please try again.", foreground="red")
            except sr.RequestError as e:
                print(f"Could not request results from MAB.AI Speech Recognition service; {e}")
                self.status_message_label.config(text="Error connecting to Google Speech Recognition service.", foreground="red")

if __name__ == "__main__":
    root = tk.Tk()
    app = SpeechRecognitionApp(root)
    root.mainloop()
