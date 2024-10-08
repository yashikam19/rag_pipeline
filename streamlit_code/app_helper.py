import re
import streamlit as st
import os
import base64
import requests
import io
from pydub import AudioSegment
import time

def text_to_speech(user_input):
    url = "https://api.sarvam.ai/text-to-speech"
    api_key = "590cc1c5-05e6-4220-98a2-bd4f5f86d3fe"
    headers = {
        'API-Subscription-Key': api_key
    }

    # Split user input into chunks of 500 characters
    chunk_size = 400
    chunks = [user_input[i:i + chunk_size] for i in range(0, len(user_input), chunk_size)]

    audio_segments = []

    for chunk in chunks:
        # Prepare the payload with user input
        payload = {
            "inputs": [chunk],
            "target_language_code": "en-IN",
            "speaker": "arvind",
            "pitch": 0,
            "pace": 1.1,
            "loudness": 1.5,
            "speech_sample_rate": 8000,
            "enable_preprocessing": True,
            "model": "bulbul:v1"
        }
        print(chunk)
        print("--"*50)
        # Make a POST request to the API
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            res = response.json()
            base64_string = res['audios'][0]

            # Decode the Base64 string
            audio_data = base64.b64decode(base64_string)

            # Create an audio file in BytesIO and append to the list
            audio_bytes = io.BytesIO(audio_data)
            audio_segments.append(AudioSegment.from_file(audio_bytes, format="wav"))
        else:
            st.error("Failed to convert text to speech for one of the chunks. Please try again.")
            return

    # Combine all audio segments
    if audio_segments:
        combined_audio = audio_segments[0]
        for segment in audio_segments[1:]:
            combined_audio += segment

        # Export combined audio to BytesIO
        combined_audio_io = io.BytesIO()
        combined_audio.export(combined_audio_io, format='wav')
        combined_audio_io.seek(0)  # Reset cursor to the beginning

        # Get audio data as base64 for JavaScript playback
        audio_base64 = base64.b64encode(combined_audio_io.read()).decode('utf-8')

        # JavaScript for audio playback
        audio_html = f"""
            <audio id="background-audio" autoplay>
                <source src="data:audio/wav;base64,{audio_base64}" type="audio/wav">
            </audio>
            <script>
                var audio = document.getElementById('background-audio');
                audio.play();
            </script>
        """

        # Display the audio HTML
        st.markdown(audio_html, unsafe_allow_html=True)
    else:
        st.error("No audio segments to combine.")

def preprocess_text(text: str) -> str:
    # Remove markdown bold formatting (**)
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Remove Markdown headers (### Header)
    text = re.sub(r'###\s*', '', text)
    return text.replace('\n', ' ')