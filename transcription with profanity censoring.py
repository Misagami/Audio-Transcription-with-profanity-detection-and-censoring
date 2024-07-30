import tkinter as tk
from tkinter import scrolledtext
from vosk import Model, KaldiRecognizer
import pyaudio
import better_profanity
import json

class TranscriptionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Speech Transcription with Profanity Filter")
        
        self.text_area = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=40, height=10)
        self.text_area.pack(pady=10)
        
        self.start_button = tk.Button(root, text="Start Transcription", command=self.start_transcription)
        self.start_button.pack(pady=5)
        
        self.stop_button = tk.Button(root, text="Stop Transcription", command=self.stop_transcription, state=tk.DISABLED)
        self.stop_button.pack(pady=5)
        
        self.transcription_running = False
        self.model = Model(r'C:\My folder\Projects\Transcription with  profanity detection vosk\vosk-model-small-en-us-0.15')
        self.recognizer = KaldiRecognizer(self.model, 16000)
        self.profanity_filter = better_profanity.Profanity()
        self.cap = pyaudio.PyAudio()
        self.stream = self.cap.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=2048)
    
    def start_transcription(self):
        self.transcription_running = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        while self.transcription_running:
            try:
                data = self.stream.read(4096)
                if len(data) == 0:
                    break

                if self.recognizer.AcceptWaveform(data):
                    result = self.recognizer.Result()
                    result_dict = json.loads(result)
                    transcribed_text = result_dict["text"]
                    if self.profanity_filter.contains_profanity(transcribed_text):
                        transcribed_text = self.profanity_filter.censor(transcribed_text)
                    self.text_area.insert(tk.END, transcribed_text + "\n")
                    self.text_area.see(tk.END)
                    self.root.update()
            except Exception as e:
                print("Error:", e)
                break
    
    def stop_transcription(self):
        self.transcription_running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

        print("Stopping the transcription...")
        self.stream.stop_stream()
        self.stream.close()
        self.cap.terminate()

if __name__ == "__main__":
    root = tk.Tk()
    app = TranscriptionApp(root)
    root.mainloop()
