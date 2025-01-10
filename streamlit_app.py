import streamlit as st
from gtts import gTTS
from io import BytesIO
import tempfile
import os
import ffmpeg
from PIL import Image

def single_slide_tts_to_mp4():
    st.header("Single-Slide TTS to MP4")

    uploaded_file = st.file_uploader("Upload your slide image (JPG or PNG):", type=["jpg", "jpeg", "png"])
    text_input = st.text_area("Enter the text for this slide (TTS):")

    if st.button("Generate MP4"):
        if not uploaded_file:
            st.warning("Please upload an image slide.")
            return
        if not text_input.strip():
            st.warning("Please enter some text.")
            return

        with Image.open(uploaded_file) as img:
            if img.mode != "RGB":
                img = img.convert("RGB")

            width, height = img.size
            new_width = width if width % 2 == 0 else width - 1
            new_height = height if height % 2 == 0 else height - 1
            img = img.resize((new_width, new_height))

            temp_image_path = os.path.join(tempfile.gettempdir(), "uploaded_slide.jpg")
            img.save(temp_image_path)

        tts = gTTS(text_input, lang="en")
        audio_fp = BytesIO()
        tts.write_to_fp(audio_fp)
        audio_fp.seek(0)

        temp_audio_path = os.path.join(tempfile.gettempdir(), "tts_audio.mp3")
        with open(temp_audio_path, "wb") as f:
            f.write(audio_fp.read())

        temp_output_path = os.path.join(tempfile.gettempdir(), "tts_slide.mp4")
        try:
            input_image = ffmpeg.input(temp_image_path, loop=1, framerate=1)
            input_audio = ffmpeg.input(temp_audio_path)
            ffmpeg.output(
                input_image,
                input_audio,
                temp_output_path,
                vcodec='libx264',
                pix_fmt='yuv420p',
                shortest=None,
                acodec='aac',
                audio_bitrate='192k'
            ).run(overwrite_output=True)
        except ffmpeg.Error as e:
            error_message = e.stderr.decode('utf-8', 'replace') if e.stderr else str(e)
            st.error(f"Error running ffmpeg: {error_message}")
            return

        with open(temp_output_path, "rb") as f:
            mp4_data = f.read()

        st.video(mp4_data)
        st.download_button(label="Download MP4", data=mp4_data, file_name="tts_slide.mp4", mime="video/mp4")

        os.remove(temp_image_path)
        os.remove(temp_audio_path)
        os.remove(temp_output_path)

def main():
    st.title("Single-Slide TTS to MP4")
    single_slide_tts_to_mp4()

if __name__ == "__main__":
    main()
