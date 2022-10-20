import whisper
import streamlit as st
import time
import os
from pathlib import Path

path = Path("audio")
model = whisper.load_model("base")


def transcriber(audio_path):
    audio = whisper.load_audio(audio_path)
    result = model.transcribe(audio)
    results = result["segments"]
    return results


def convert(seconds):
    return time.strftime("%H:%M:%S", time.gmtime(seconds))


def format_transcript(results):
    final_transcript = []
    for output in results:
        timestamp = f'{convert(output["start"])}'
        transcribed = output["text"]
        section = f"[{timestamp[3:]}]{transcribed}\n"
        final_transcript.append(section)
    return final_transcript


def list_to_plain_text(list_entry):
    plain_text = ""
    for i in list_entry:
        plain_text += str(i)
    return plain_text


@st.cache
def write_to_file(text, filename):
    with open(filename, 'w') as f:
        document = f.write(text)
    return document


st.header("Transcription made easier.")
uploaded_file = st.file_uploader(label="Upload the audio-file you would like to transcribe.",
                                 type=['mp3', 'm4a', 'wav'])


# TODO connect app to database for temp storage of audiofile.
def start_upload_and_transcribe(new_file):
    if new_file is not None:
        bytes_data = new_file.getvalue()
        with open(os.path.join("audio", new_file.name), "wb") as file:
            file.write(uploaded_file.getbuffer())
        with st.spinner("Working on the transcription..."):
            transcript = transcriber(file.name)
            formatted_transcript = format_transcript(transcript)
            transcript_result_to_display = list_to_plain_text(formatted_transcript)
            final_text = st.text_area(label="Your Transcript:", value=transcript_result_to_display, height=400)
            st.download_button(label="Download Text as txt",
                               data=final_text,
                               file_name="Transcript.docx")
        if bytes_data:
            st.audio(bytes_data, format='audio/wav')
            st.success("Done!")


start_upload_and_transcribe(uploaded_file)
