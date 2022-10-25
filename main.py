import whisper
import streamlit as st
import os
from pathlib import Path
import time

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
    with open(os.path.join("transcripts", "Transcript.txt"), 'w') as f:
        f.write(text)
        delete_files("audio")
    st.session_state.current_text = text
    text_area(st.session_state.current_text)


def update_file():
    print(f"Entering the update function. 1")
    if st.session_state.current_text is not None:
        with open(os.path.join("transcripts", "Transcript.txt"), 'w') as f:
            f.write(st.session_state.current_text)
            print(f"Leaving the update function.2")
    else:
        pass


def delete_files(my_path):
    for file in os.listdir(my_path):
        file_path = os.path.join(path, file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
        except Exception as e:
            print(e)


def text_area(text):
    with tab2:
        print("Entering text area. 3")
        running_text = st.text_area(label="Your Transcript:",
                                    value=text,
                                    height=500)

        col1, col2, col3 = st.columns(3, gap="small")
        with col1:
            st.download_button(
                label="Download As .txt file.",
                data=running_text,
                file_name="YourTranscript.txt",
                on_click=update_file()
            )
        with col2:
            st.download_button(
                label="Download As .docx file.",
                data=running_text,
                file_name="YourTranscript.docx",
                on_click=update_file()
            )

        with col3:
            if st.button(label="Start A new Transcription."):
                delete_files("audio")
                delete_files("transcripts")
                for key in st.session_state.keys():
                    del st.session_state[key]

        bytes_data = st.session_state.new_audio.getvalue()

        if bytes_data:
            st.audio(st.session_state.new_audio.getvalue(), format='audio/wav')
            print("Leaving text area. 4")
            print(running_text)


def transcribe_and_prepare_audio(new_file):
    with tab2:
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


st.set_page_config(
    page_title="My Personal Transcriber.",
    layout="wide"
)
st.header("Transcription made easier.")
tab1, tab2 = st.tabs(["Upload", "Transcript Document"])

with tab1:
    if "first_run" not in st.session_state:
        st.session_state["first_run"] = None

    uploaded_file = st.file_uploader(label="Upload the audio-file you would like to transcribe.",
                                     type=['mp3', 'm4a', 'wav'])

    if st.session_state.first_run is None:
        print("Fresh Start")
        if "new_audio" not in st.session_state:
            st.session_state["new_audio"] = None

        if "current_text" not in st.session_state:
            st.session_state["current_text"] = None

        transcribe_and_prepare_audio(uploaded_file)
    else:
        text_area(st.session_state.current_text)
