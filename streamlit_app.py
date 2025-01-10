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
            (
                ffmpeg
                .input(temp_image_path, loop=1, framerate=1)
                .input(temp_audio_path)
                .output(temp_output_path, vcodec='libx264', acodec='aac', pix_fmt='yuv420p', shortest=None)
                .run()
            )
        except ffmpeg.Error as e:
            st.error(f"Error running ffmpeg: {e.stderr.decode()}")
            return

        with open(temp_output_path, "rb") as f:
            mp4_data = f.read()

        st.video(mp4_data)
        st.download_button(label="Download MP4", data=mp4_data, file_name="tts_slide.mp4", mime="video/mp4")

        os.remove(temp_image_path)
        os.remove(temp_audio_path)
        os.remove(temp_output_path)

def video_clipper_and_combiner():
    st.header("Video Clipper and Combiner (FFmpeg)")

    st.write("Upload multiple video files (e.g., .mp4, .mov, .avi) in the order you want them concatenated.")

    uploaded_files = st.file_uploader(label="Choose your video files", type=["mp4", "mov", "avi"], accept_multiple_files=True)

    if st.button("Combine Videos"):
        if not uploaded_files:
            st.warning("Please upload at least one video file.")
            return

        temp_dir = tempfile.mkdtemp()
        video_paths = []

        for uploaded_file in uploaded_files:
            temp_file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.read())
            video_paths.append(temp_file_path)

        filelist_path = os.path.join(temp_dir, "filelist.txt")
        with open(filelist_path, "w") as f:
            for path in video_paths:
                f.write(f"file '{path}'\n")

        output_path = os.path.join(temp_dir, "combined_video.mp4")

        try:
            (
                ffmpeg
                .input(filelist_path, format='concat', safe=0)
                .output(output_path, c='copy')
                .run()
            )
            st.success("Videos have been combined successfully!")

            with open(output_path, "rb") as f:
                st.download_button(label="Download Combined Video", data=f, file_name="final_combined_video.mp4", mime="video/mp4")
        except ffmpeg.Error as e:
            st.error("Error while combining videos:")
            st.error(e.stderr.decode())

def main():
    st.title("Two-in-One Streamlit App")

    app_choice = st.sidebar.selectbox("Choose a feature:", ["Single-Slide TTS to MP4", "Video Clipper and Combiner"])

    if app_choice == "Single-Slide TTS to MP4":
        single_slide_tts_to_mp4()
    else:
        video_clipper_and_combiner()

if __name__ == "__main__":
    main()
