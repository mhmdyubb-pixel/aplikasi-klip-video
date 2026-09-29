import streamlit as st
import yt_dlp
import os
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

st.set_page_config(page_title="Klip YouTube", page_icon="✂️")
st.title("✂️ Aplikasi Klip YouTube Otomatis")
st.write("Sistem otomatis memotong 30 detik bagian tengah video.")

url = st.text_input("🔗 Paste Link YouTube di sini:")

if st.button("Buat Klip Sekarang!"):
    if url:
        with st.spinner("Sedang mengunduh dan memotong video... Mohon tunggu!"):
            ydl_opts = {'format': 'best[ext=mp4]', 'outtmpl': 'video_asli.mp4', 'quiet': True}
            try:
                # 1. Download Video
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    durasi_total = info.get('duration', 0)
                
                # 2. Hitung Waktu Tengah
                waktu_mulai = max(0, (durasi_total // 2) - 15)
                waktu_selesai = min(durasi_total, waktu_mulai + 30)
                
                # 3. Potong Video
                ffmpeg_extract_subclip("video_asli.mp4", waktu_mulai, waktu_selesai, targetname="hasil.mp4")
                
                st.success("✅ Video berhasil dipotong!")
                
                # 4. Tampilkan Tombol Download
                with open("hasil.mp4", "rb") as file:
                    st.download_button(label="⬇️ Download Video Hasil Klip", data=file, file_name="klip_youtube.mp4", mime="video/mp4")
                    
                # Bersihkan sistem server
                if os.path.exists("video_asli.mp4"): os.remove("video_asli.mp4")
            except Exception as e:
                st.error(f"❌ Terjadi kesalahan: Pastikan link benar atau coba video lain.")
    else:
        st.warning("Harap masukkan link terlebih dahulu!")