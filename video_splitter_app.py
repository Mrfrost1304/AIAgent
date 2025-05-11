import os
import shutil
import streamlit as st
from moviepy.video.io.VideoFileClip import VideoFileClip
from zipfile import ZipFile

def split_video(video_path, chunk_length, output_dir):
    clip = VideoFileClip(video_path)
    print(f"clip type: {type(clip)}")
    print(f"hasattr subclip: {hasattr(clip, 'subclip')}")
    duration = clip.duration
    os.makedirs(output_dir, exist_ok=True)
    
    parts = []
    chunk_length = int(chunk_length)  # Convert chunk_length to int to avoid TypeError in range
    for i in range(0, int(duration), chunk_length):
        subclip = clip.subclipped(i, min(i + chunk_length, duration))
        filename = os.path.join(output_dir, f"part_{i//chunk_length + 1:03d}.mp4")
        subclip.write_videofile(filename, codec="libx264", audio_codec="aac")
        parts.append(filename)
    return parts

def zip_files(file_list, zip_name):
    with ZipFile(zip_name, 'w') as zipf:
        for file in file_list:
            zipf.write(file, os.path.basename(file))

# Streamlit UI
st.title("🎬 Movie Splitter - Chunk & Zip Your Video")
uploaded_file = st.file_uploader("Upload a movie file (mp4, mov, avi)", type=["mp4", "mov", "avi"])
chunk_length = st.number_input("Enter chunk length (in seconds)", min_value=10, max_value=600, value=60)

if uploaded_file is not None:
    with open("input_video.mp4", "wb") as f:
        f.write(uploaded_file.read())
    st.success("✅ Video uploaded successfully.")

    if st.button("Split and Download"):
        with st.spinner("Processing... Please wait."):
            output_dir = "chunks"
            zip_name = "movie_parts.zip"

            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)

            os.makedirs(output_dir, exist_ok=True)

            parts = split_video("input_video.mp4", chunk_length, output_dir)
            zip_files(parts, zip_name)

        with open(zip_name, "rb") as f:
            st.download_button("📦 Download ZIP File", f, file_name="movie_parts.zip", mime="application/zip")

        st.success("🎉 Video has been split and zipped successfully! You can download it above.")

        # Cleanup
        os.remove("input_video.mp4")
        shutil.rmtree(output_dir)
        os.remove(zip_name)
