import streamlit as st
import os
import time
import subprocess
from openai import OpenAI

st.set_page_config(page_title="AI Video Clipper", page_icon="🤖")
st.title("🤖 Aplikasi Potong Video & Subtitel AI")
st.write("Upload video, masukkan API Key OpenAI, dan biarkan AI membuat subtitel serta klip otomatis.")

# Input API Key untuk keamanan & kestabilan cloud
api_key = st.text_input("🔑 Masukkan OpenAI API Key Anda:", type="password")

# 1. Fitur Upload Video
uploaded_file = st.file_uploader("📂 Pilih file video (MP4, MOV):", type=['mp4', 'mov'])

if uploaded_file is not None:
    st.success("✅ Video berhasil dimuat!")
    st.video(uploaded_file)
    
    st.divider()
    mode_ai = st.checkbox("✨ Aktifkan Mode AI (Auto-Subitle & Smart Clip)")
    
    if mode_ai:
        st.info("💡 Mode AI aktif: AI akan mentranskrip suara video menjadi teks dan membuat subtitel otomatis.")
        
    if st.button("🚀 Proses Video Sekarang!"):
        if not api_key and mode_ai:
            st.error("❌ Harap masukkan OpenAI API Key terlebih dahulu jika menggunakan Mode AI!")
        else:
            with st.spinner("Sedang memproses video dengan AI... Mohon tunggu!"):
                id_unik = str(int(time.time()))
                file_input = f"input_{id_unik}.mp4"
                file_output = f"output_{id_unik}.mp4"
                
                try:
                    # Simpan file upload ke server
                    with open(file_input, "wb") as f:
                        f.write(uploaded_file.read())
                        
                    if mode_ai:
                        # Inisialisasi klien OpenAI
                        client = OpenAI(api_key=api_key)
                        
                        st.write("🎙️ Sedang mengekstrak audio untuk transkrip AI...")
                        audio_file = f"audio_{id_unik}.mp3"
                        
                        # Ekstrak audio dari video pakai FFmpeg
                        subprocess.run(["ffmpeg", "-y", "-i", file_input, "-q:a", "0", "-map", "a", audio_file], check=True)
                        
                        st.write("✍️ AI sedang mendengarkan dan membuat subtitel...")
                        with open(audio_file, "rb") as audio:
                            transcript = client.audio.transcriptions.create(
                                model="whisper-1",
                                file=audio,
                                response_format="srt"
                            )
                            
                        # Simpan file subtitel .srt
                        srt_file = f"sub_{id_unik}.srt"
                        with open(srt_file, "w", encoding="utf-8") as f:
                            f.write(transcript)
                            
                        st.write("🎨 Membakar subtitel ke dalam video...")
                        cmd = [
                            "ffmpeg", "-y",
                            "-i", file_input,
                            "-vf", f"subtitles={srt_file}:force_style='Fontsize=24,PrimaryColour=&H00FFFF&'",
                            file_output
                        ]
                        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                        
                        # Bersihkan file audio & srt sementara
                        if os.path.exists(audio_file): os.remove(audio_file)
                        if os.path.exists(srt_file): os.remove(srt_file)
                        
                    else:
                        # Mode Standar (Potong biasa 30 detik pertama)
                        cmd = [
                            "ffmpeg", "-y", 
                            "-i", file_input, 
                            "-ss", "0", "-to", "30", 
                            "-c:v", "copy", "-c:a", "copy", 
                            file_output
                        ]
                        subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                    
                    st.success("🎉 Berhasil! Video dan subtitel AI siap.")
                    st.video(file_output)
                    
                    with open(file_output, "rb") as f:
                        st.download_button(
                            label="⬇️ Download Video Hasil AI",
                            data=f.read(),
                            file_name=f"ai_klip_{id_unik}.mp4",
                            mime="video/mp4"
                        )
                        
                except Exception as e:
                    st.error(f"❌ Terjadi kesalahan: {e}")
                finally:
                    if os.path.exists(file_input): 
                        try: os.remove(file_input) 
                        except: pass
                    if os.path.exists(file_output): 
                        try: os.remove(file_output) 
                        except: pass
