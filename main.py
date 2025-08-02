from flask import Flask, request
import os, openai, requests
from dotenv import load_dotenv
from pydub import AudioSegment
from io import BytesIO

load_dotenv()
app = Flask(__name__)
openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route("/")
def home():
    return "Bot is live!"

@app.route("/bot", methods=["POST"])
def bot():
    msg = request.form.get("Body")
    media_url = request.form.get("MediaUrl0")
    media_type = request.form.get("MediaContentType0")
    response = ""
    if msg:
        reply = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": msg}]
        )
        response = reply['choices'][0]['message']['content']
    elif media_url and "audio" in media_type:
        audio_data = requests.get(media_url).content
        audio = AudioSegment.from_file(BytesIO(audio_data), format="ogg")
        audio.export("/tmp/voice.wav", format="wav")
        with open("/tmp/voice.wav", "rb") as audio_file:
            transcript = openai.Audio.transcribe("whisper-1", audio_file)
            text = transcript["text"]
            reply = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[{"role": "user", "content": text}]
            )
            response = reply['choices'][0]['message']['content']
    return f"<Response><Message>{response}</Message></Response>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
