import whisper
import streamlit as st
import os
from pathlib import Path
import time
import pyautogui

path = Path("audio")
path_transcript = Path("transcripts")
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
    st.session_state.current_text = text
    text_area(st.session_state.current_text)


def delete_file():
    file_name = st.session_state.new_audio.name
    current_directory = os.getcwd()
    audio_folder = os.path.join(current_directory, "audio")
    file_path = os.path.join(audio_folder, file_name)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"{file_name} has been deleted successfully from {audio_folder}")
    else:
        print(f"{file_name} does not exist in {audio_folder}")

def apply_changes():
    pyautogui.hotkey('ctrl', 'enter')

def text_area(text):
    with tab2:
        running_text = st.text_area(label="Your Transcript:",
                                    value=text,
                                    height=500)

        col1, col2, col3 = st.columns(3, gap="small")
        with col3:
            st.download_button(
                label="Download transcript",
                data=running_text,
                file_name="YourTranscript.docx",
                on_click=apply_changes
            )
        with col2:
            st.button(label="Delete Audio file",
                      on_click=delete_file
                      )
        with col1:
            st.button(label="Save Changes",
                      on_click=apply_changes)

        bytes_data = st.session_state.new_audio.getvalue()

        if bytes_data:
            st.audio(st.session_state.new_audio.getvalue(), format='audio/wav')

def transcribe_and_prepare_audio(new_file):
    with tab2:
        st.session_state["new_audio"] = new_file
        if st.session_state.new_audio is not None:
            with open(os.path.join("audio", st.session_state.new_audio.name), "wb") as file:
                file.write(st.session_state.new_audio.getbuffer())

                if st.session_state.first_run is None:
                    st.info(f'Working on your transcription. This may take a few minutes...', icon='ℹ️')
                    transcript = transcriber(file.name)
                    formatted_transcript = format_transcript(transcript)
                    transcript_result_to_display = list_to_plain_text(formatted_transcript)
                    write_to_file(transcript_result_to_display)
                    st.session_state.first_run = 1


st.set_page_config(
    page_title="My Personal Transcriber.",
    layout="centered"
)
st.header("Transcription made easier.")
tab1, tab2 = st.tabs(["Upload", "Transcript Tab"])

with tab1:
    if "first_run" not in st.session_state:
        st.session_state["first_run"] = None

    uploaded_file = st.file_uploader(label="Upload the audio-file you would like to transcribe.",
                                     type=['mp3', 'm4a', 'wav'])

    if uploaded_file:
        st.write("After uploading your audio file, go to the Transcript Tab.")

    if st.session_state.first_run is None:
        print("Fresh Start")
        if "new_audio" not in st.session_state:
            st.session_state["new_audio"] = None

        if "current_text" not in st.session_state:
            st.session_state["current_text"] = None


        transcribe_and_prepare_audio(uploaded_file)

    else:
        text_area(st.session_state.current_text)
