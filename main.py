import whisper
import streamlit as st
import time
import os
from pathlib import Path
import random

path = Path("audio")
# path_two = Path("transcripts")
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


def write_to_file(text):
    with open(os.path.join("transcripts", "Transcript.txt"), 'w') as f:
        f.write(text)
        delete_files("audio")
    text_area()


def delete_files(my_path):
    for file in os.listdir(my_path):
        file_path = os.path.join(path, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)



def text_area():
    # st.text_area(label="Your Transcript:", value=text, height=400)
    with open("transcripts/Transcript.txt") as file:
        extract = file.read()
    text = st.text_area(label="Your Transcript:", value=extract, height=400)
    with open(os.path.join("transcripts", "Transcript.txt"), 'w') as f:
        f.write(text)

    bytes_data = st.session_state.new_audio.getvalue()

    if bytes_data:
        st.audio(st.session_state.new_audio.getvalue(), format='audio/wav')


def transcribe_and_prepare_audio(new_file):
    st.session_state["new_audio"] = new_file
    if st.session_state.new_audio is not None:
        with open(os.path.join("audio", st.session_state.new_audio.name), "wb") as file:
            file.write(st.session_state.new_audio.getbuffer())

            if st.session_state.first_run is None:
                st.info('Working on you transcription. This may take a few minutes...', icon="ℹ")
                transcript = transcriber(file.name)
                formatted_transcript = format_transcript(transcript)
                transcript_result_to_display = list_to_plain_text(formatted_transcript)
                write_to_file(transcript_result_to_display)
                st.session_state.first_run = 1


if "new_audio" not in st.session_state:
    st.session_state["new_audio"] = None

if "current_text" not in st.session_state:
    st.session_state["current_text"] = None

if "first_run" not in st.session_state:
    st.session_state["first_run"] = None

st.set_page_config(
    page_title="Personal Transcriber.",
    layout="centered",
    menu_items={
        "About": "# This is a test."
    }
)

st.header("Transcription made easier.")
uploaded_file = st.file_uploader(label="Upload the audio-file you would like to transcribe.",
                                 type=['mp3', 'm4a', 'wav'])

if st.session_state.first_run is None:
    transcribe_and_prepare_audio(uploaded_file)
else:
    text_area()
