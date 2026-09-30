import streamlit as st
import yt_dlp
import os
import time
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

st.set_page_config(page_title="Klip YouTube", page_icon="✂️")
st.title("✂️ Aplikasi Klip YouTube Otomatis")
st.write("Sistem otomatis memotong 30 detik bagian tengah video.")

url = st.text_input("🔗 Paste Link YouTube di sini:")

if st.button("Buat Klip Sekarang!"):
    if url:
        url = url.strip()
        
        with st.spinner("Sedang mengunduh dan memotong video... Mohon tunggu!"):
            id_unik = str(int(time.time()))
            file_asli = f"video_asli_{id_unik}.mp4"
            file_hasil = f"hasil_{id_unik}.mp4"
            
            # --- BAGIAN YANG DIPERBAIKI ---
            # Mengizinkan sistem mengambil video dan audio terpisah lalu digabung menjadi mp4
            ydl_opts = {
                'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best', 
                'outtmpl': file_asli, 
                'quiet': True,
                'noplaylist': True,
                'merge_output_format': 'mp4'
            }
            # ------------------------------
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    durasi_total = info.get('duration', 0)
                
                if durasi_total == 0:
                    st.error("❌ Gagal membaca durasi. (Pastikan ini bukan video Live Stream).")
                else:
                    waktu_mulai = max(0, (durasi_total // 2) - 15)
                    waktu_selesai = min(durasi_total, waktu_mulai + 30)
                    
                    ffmpeg_extract_subclip(file_asli, waktu_mulai, waktu_selesai, targetname=file_hasil)
                    
                    st.success("✅ Video berhasil dipotong!")
                    
                    with open(file_hasil, "rb") as file:
                        video_bytes = file.read()
                        
                    st.download_button(
                        label="⬇️ Download Video Hasil Klip", 
                        data=video_bytes, 
                        file_name=f"klip_youtube_{id_unik}.mp4", 
                        mime="video/mp4"
                    )
                    
            except Exception as e:
                st.error(f"❌ Gagal memproses: {e}")
                
            finally:
                if os.path.exists(file_asli): 
                    os.remove(file_asli)
                if os.path.exists(file_hasil): 
                    os.remove(file_hasil)
    else:
        st.warning("Harap masukkan link terlebih dahulu!")
